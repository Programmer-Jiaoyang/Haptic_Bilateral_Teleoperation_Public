import sys
print("Python executable:", sys.executable, flush=True)
print("Python version:", sys.version, flush=True)
print("Version 1.0.1", flush=True)

import rclpy
import struct
import socket
import time

from rclpy.node import Node
from std_msgs.msg import Float32MultiArray, Float64

# Robot IP and port
robot_ip = '192.168.1.245'
robot_port = 30000

def bytes_to_fp32(bytes_data, is_big_endian=False):
    return struct.unpack('>f' if is_big_endian else '<f', bytes_data)[0]

def bytes_to_fp32_list(bytes_data, n=0, is_big_endian=False):
    ret = []
    count = n if n > 0 else len(bytes_data) // 4
    for i in range(count):
        ret.append(bytes_to_fp32(bytes_data[i * 4: i * 4 + 4], is_big_endian))
    return ret

def bytes_to_u32(data):
    data_u32 = data[0] << 24 | data[1] << 16 | data[2] << 8 | data[3]
    return data_u32

class Timer:
    def __init__(self):
        self._offset_ns = time.time_ns() - time.perf_counter_ns()

    def time_ns(self):
        return self._offset_ns + time.perf_counter_ns()

timer = Timer()

class RobotStatePublisher(Node):
    def __init__(self):
        super().__init__('robot_state_publisher')
        self.pub_pos = self.create_publisher(Float32MultiArray, '/xarm_joint_positions', 10)
        self.pub_vel = self.create_publisher(Float32MultiArray, '/xarm_joint_velocities', 10)
        self.pub_tor = self.create_publisher(Float32MultiArray, '/xarm_joint_torques', 10)
        self.pub_cur = self.create_publisher(Float32MultiArray, '/xarm_joint_currents', 10)
        self.pub_timestamp = self.create_publisher(Float64, '/xarm_timestamp', 10)
        self.timer_period = 0.01
        self.timer = self.create_timer(self.timer_period, self.publish_state)

        # Connect to robot
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setblocking(True)
        self.sock.settimeout(1)
        self.sock.connect((robot_ip, robot_port))
        
        # Read initial size
        buffer = self.sock.recv(4)
        while len(buffer) < 4:
            buffer += self.sock.recv(4 - len(buffer))
        self.size = bytes_to_u32(buffer[:4])
        self.buffer = b''

        self.get_logger().info("RobotStatePublisher initialized!")

    def publish_state(self):
        try:
            self.buffer += self.sock.recv(self.size - len(self.buffer))
            timetemp = float(timer.time_ns())
            if len(self.buffer) < self.size:
                return
            data = self.buffer[:self.size]
            self.buffer = self.buffer[self.size:]

            angle = bytes_to_fp32_list(data[116:144])
            velocity = bytes_to_fp32_list(data[144:172])
            current = bytes_to_fp32_list(data[200:228])
            torque = bytes_to_fp32_list(data[228:256])
            

            msg_pos = Float32MultiArray(data=angle)
            msg_vel = Float32MultiArray(data=velocity)
            msg_cur = Float32MultiArray(data=current)
            msg_tor = Float32MultiArray(data=torque)
            msg_time = Float64(data=timetemp)

            # Publish
            self.pub_pos.publish(msg_pos)
            self.pub_vel.publish(msg_vel)
            self.pub_cur.publish(msg_cur)
            self.pub_tor.publish(msg_tor)
            self.pub_timestamp.publish(msg_time)

        except Exception as e:
            self.get_logger().error(f"Error: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = RobotStatePublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()