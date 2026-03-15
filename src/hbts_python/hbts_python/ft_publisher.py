import sys
print("Python executable:", sys.executable, flush=True)
print("Python version:", sys.version, flush=True)
print("Version 1.0.6", flush=True)

import rclpy
import time
import libscrc
import serial
import minimalmodbus as mm
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray,Float64

#Communication setup
BAUDRATE=19200
BYTESIZE=8
PARITY="N"
STOPBITS=1
TIMEOUT=1

SLAVEADDRESS=9

def forceFromSerialMessage(serialMessage,zeroRef=[0,0,0,0,0,0]):
  """Return a list with force and torque values [Fx,Fy,Fz,Tx,Ty,Tz] correcponding to the dataArray
  
  Parameters
  ----------
  serialMessage:
    bytearray which contents the serial message send by the FT300. 
    [0x20,0x4e,LSBdata1,MSBdata2,...,LSBdata6,MSBdata6,crc1,crc2]
    Check FT300 manual for details.
  zeroRef:
    list with force and torque values [Fx,Fy,Fz,Tx,Ty,Tz] use the set the zero reference of the sensor.
  
  Return
  ------
  forceTorque:
    list with force and torque values [Fx,Fy,Fz,Tx,Ty,Tz] correcponding to the dataArray
  """
  #Initialize variable
  forceTorque=[0,0,0,0,0,0]
  
  #converte bytearray values to integer. Apply the zero offset and round at 2 decimals
  forceTorque[0]=float(round(int.from_bytes(serialMessage[2:4], byteorder='little', signed=True)/100-zeroRef[0],2))
  forceTorque[1]=float(round(int.from_bytes(serialMessage[4:6], byteorder='little', signed=True)/100-zeroRef[1],2))
  forceTorque[2]=float(round(int.from_bytes(serialMessage[6:8], byteorder='little', signed=True)/100-zeroRef[2],2))
  forceTorque[3]=float(round(int.from_bytes(serialMessage[8:10], byteorder='little', signed=True)/1000-zeroRef[3],2))
  forceTorque[4]=float(round(int.from_bytes(serialMessage[10:12], byteorder='little', signed=True)/1000-zeroRef[4],2))
  forceTorque[5]=float(round(int.from_bytes(serialMessage[12:14], byteorder='little', signed=True)/1000-zeroRef[5],2))
  
  return forceTorque

def crcCheck(serialMessage):
  """Check if the serial message have a valid CRC.
  
  Parameters
  -----------
  serialMessage:
    bytearray which contents the serial message send by the FT300. 
    [0x20,0x4e,LSBdata1,MSBdata2,...,LSBdata6,MSBdata6,crc1,crc2]
    Check FT300 manual for details.
    
  Return
  ------
  checkResult:
    bool, return True if the message have a valid CRC and False if not.
  """
  checkResult = False
  
  #CRC from serial message
  crc = int.from_bytes(serialMessage[14:16], byteorder='little', signed=False)
  #calculated CRC
  crcCalc = libscrc.modbus(serialMessage[0:14])
  
  if crc == crcCalc:
    checkResult = True
  
  return checkResult

class Timer:
    def __init__(self):
        self._offset_ns = time.time_ns() - time.perf_counter_ns()

    def time_ns(self):
        return self._offset_ns + time.perf_counter_ns()

timer = Timer()

class FTSensorPublisher(Node):
    def __init__(self):
        super().__init__('ft_sensor_publisher')
        self.declare_parameter('portname', '/dev/ttyUSB0')
        self.portname = self.get_parameter('portname').get_parameter_value().string_value

        # Publishers
        self.pub_ft = self.create_publisher(Float32MultiArray, '/ft_data', 10)
        self.pub_time = self.create_publisher(Float64, '/ft_timestamp', 10)

        # Timer for periodic publishing
        self.timer_period = 0.01  
        self.timer = self.create_timer(self.timer_period, self.publish_ft)

        # Desactivate streaming mode
        ser = serial.Serial(port=self.portname, baudrate=BAUDRATE, bytesize=BYTESIZE, parity=PARITY, stopbits=STOPBITS, timeout=TIMEOUT)
        packet = bytearray()
        sendCount=0
        while sendCount<50:
          packet.append(0xff)
          sendCount=sendCount+1
        ser.write(packet)
        ser.close()
        del packet
        del sendCount    
        del ser
        
        print("Streaming mode deactivated. Starting FT300 initialization...", flush=True)
        time.sleep(2)
        print("Start publishing FT data at topic /ft_data and timestamp at topic /ft_timestamp", flush=True)

        # Activate streaming mode
        mm.BAUDRATE=BAUDRATE
        mm.BYTESIZE=BYTESIZE
        mm.PARITY=PARITY
        mm.STOPBITS=STOPBITS
        mm.TIMEOUT=TIMEOUT

        # Create FT300 object
        ft300=mm.Instrument(self.portname, slaveaddress=SLAVEADDRESS)
        ft300.close_port_after_each_call=True

        # Write 0x0200 in 410 register to start streaming
        ft300.write_register(410,0x0200)
        del ft300

        # Open serial connection
        self.ser=serial.Serial(self.portname, baudrate=BAUDRATE, bytesize=BYTESIZE, parity=PARITY, stopbits=STOPBITS, timeout=TIMEOUT)

        # Bytes use to itendify the beginning of the serial message
        self.STARTBYTES = bytes([0x20,0x4e])
        
        # Read serial buffer until founding the bytes [0x20,0x4e]
        # First serial reading.
        # This message in uncomplete in most cases so it is ignored.
        data = self.ser.read_until(self.STARTBYTES)
        
        # Second serial reading.
        # This message is use to make the zero of the sensor.
        data = self.ser.read_until(self.STARTBYTES)

        # Convert from byte to bytearray
        dataArray = bytearray(data)

        # Delete the end bytes [0x20,0x4e] and place it at the beginning of the bytearray
        dataArray = self.STARTBYTES+dataArray[:-2]
        
        # Referece for zero readings
        self.zeroRef = forceFromSerialMessage(dataArray)

        # Check if the serial message have a valid CRC
        if crcCheck(dataArray) is False:
          raise Exception("CRC ERROR: Serial message and the CRC does not match")

    def publish_ft(self):
        try:
            data = self.ser.read_until(self.STARTBYTES)
            t_ns = float(timer.time_ns())
            dataArray = bytearray(data)
            dataArray = self.STARTBYTES + dataArray[:-2]

            if crcCheck(dataArray) is False:
                self.get_logger().warn("CRC ERROR: ignoring this packet")
                return

            ft_values = forceFromSerialMessage(dataArray, self.zeroRef)

            # Publish
            self.pub_ft.publish(Float32MultiArray(data=ft_values))
            self.pub_time.publish(Float64(data=t_ns))

        except Exception as e:
            self.get_logger().error(f"Serial read error: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = FTSensorPublisher()
    rclpy.spin(node)
    node.ser.close()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()