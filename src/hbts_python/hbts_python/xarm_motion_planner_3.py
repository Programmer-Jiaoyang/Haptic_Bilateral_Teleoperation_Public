"""
ROS2 Node: Haptic to XArm
Subscribes to haptic device pose, processes it, and moves the robot in real-time. Add support for gripper.
Mapping strategy: absolute mapping
Control strategy: arm.set_servo_cartesian
"""
import sys
print("Python executable:", sys.executable, flush=True)
print("Python version:", sys.version, flush=True)
print("Version 1.0.0", flush=True)

import rclpy
import time
import numpy as np

from rclpy.node import Node
from scipy.spatial.transform import Rotation as R
from std_msgs.msg import Float32MultiArray,Float32
from xarm.wrapper import XArmAPI

# class LowPassFilter:
#     def __init__(self, alpha=0.25):
#         self.alpha = alpha
#         self.last_value = None

#     def filter(self, value):
#         value = np.array(value)
#         if self.last_value is None:
#             self.last_value = value
#             return value
#         self.last_value = self.alpha * value + (1 - self.alpha) * self.last_value
#         return self.last_value

def orientation_transformation(xarm_default_eul, haptic_eul):
    # Tool frame wrt base frame
    RotArm = R.from_euler('xyz', xarm_default_eul)
    # New pose in base frame
    RotHap = R.from_euler('xyz', haptic_eul)
    # New pose in tool frame 
    RotNew =  RotHap * RotArm
    # Euler angles in radians
    EulNew_rad = RotNew.as_euler('xyz')
    # Convert back to degrees and wrap to [-180, 180]
    EulNew_deg = (np.rad2deg(EulNew_rad) + 180) % 360 - 180
    return EulNew_deg

class HapticXArmNode(Node):
    def __init__(self):
        super().__init__('haptic_to_xarm_node')
        # Latest haptic data
        self.haptic_pos = np.zeros(3)
        self.haptic_ori = np.zeros(3)
        self.haptic_but = np.zeros(1)

        # Scale & offset
        self.scale = np.array([5, 5, 1])
        self.offset = np.array([0.415, 0, 0.345])

        # Default speed and pose
        self.xarm_speed = 30
        self.xarm_pos = [415, 0, 345, -180, 0, -130]
        
        # Default haptic pose
        self.haptic_def_pos = ([0.018854, 0.001639, -0.068857] + self.offset[0:3]) * 1000 * self.scale[0:3]
        self.haptic_def_ori = orientation_transformation(np.deg2rad(self.xarm_pos[3:6]), np.deg2rad([0, 0, 0]))

        # Motion smoother
        # self.pos_filter = LowPassFilter(alpha=0.25)

        # Ros Args
        self.declare_parameter('position_topic', '/haptic_position')
        self.declare_parameter('orientation_topic', '/haptic_orientation')
        self.declare_parameter('button_topic', '/haptic_button')
        self.declare_parameter('xarm_ip', '192.168.1.245')

        self.declare_parameter('use_orientation', True)

        self.position_topic = self.get_parameter('position_topic').get_parameter_value().string_value
        self.orientation_topic = self.get_parameter('orientation_topic').get_parameter_value().string_value
        self.button_topic = self.get_parameter('button_topic').get_parameter_value().string_value
        self.xarm_ip = self.get_parameter('xarm_ip').get_parameter_value().string_value
        
        self.use_orientation = self.get_parameter('use_orientation').get_parameter_value().bool_value
        
        # Connect robot
        self.xarm = XArmAPI(self.xarm_ip)
        self.init_robot()

        # Subscriber to haptic topic
        self.sub_pos = self.create_subscription(Float32MultiArray, self.position_topic, self.pos_cb, 10)
        self.sub_ori = self.create_subscription(Float32MultiArray, self.orientation_topic, self.ori_cb, 10)
        self.sub_btn = self.create_subscription(Float32, self.button_topic, self.button_cb, 10)
        self.sub_vel = self.create_subscription(Float32, "/speed", self.speed_cb, 10)

        # Publisher target pose
        self.pub_pos = self.create_publisher(Float32MultiArray, '/xarm_goal_position', 10)
        self.pub_ori = self.create_publisher(Float32MultiArray, '/xarm_goal_orientation', 10)

        # Timer to send robot commands at 100 Hz
        self.create_timer(0.01, self.send_robot_command)  
        self.create_timer(0.2,  self.send_gripper_command) 

    def init_robot(self):
        self.xarm.motion_enable(True)
        self.xarm.set_mode(0)
        self.xarm.set_state(0)
        self.xarm.set_position(x=self.haptic_def_pos[0], y=self.haptic_def_pos[1], z=self.haptic_def_pos[2], roll=self.haptic_def_ori[0], pitch=self.haptic_def_ori[1], yaw=self.haptic_def_ori[2], speed=50, wait=True)
        self.xarm.set_mode(1)
        self.xarm.set_state(0)
        time.sleep(1)
        self.get_logger().info("XArm initialized. Set mode to 1") 
        self.xarm.set_gripper_mode(0)
        self.xarm.set_gripper_enable(True)
        self.xarm.set_gripper_speed(5000)
        time.sleep(1)
        self.get_logger().info("XArm Gripper initialized. Set mode to 0. Speed is 5000 mm/s")
        
    def pos_cb(self, msg):
        self.haptic_pos = np.array(msg.data[:3])
        # self.haptic_pos = self.pos_filter.filter(msg.data[:3])

    def ori_cb(self, msg):
        self.haptic_ori = np.array(msg.data[:3])

    def button_cb(self, msg):
        self.haptic_but = float(msg.data)
    
    def speed_cb(self, msg):
        self.xarm_speed = float(msg.data)

    def send_robot_command(self):
        target = np.zeros(6)
        target[0:3] = (self.haptic_pos + self.offset) * 1000 *self.scale
        
        if self.use_orientation:

            # --- Orientation mapping (XYZ to ZYX) ---   
            target[3] = orientation_transformation(np.deg2rad(self.xarm_pos[3:6]), self.haptic_ori)[0]
            target[4] = orientation_transformation(np.deg2rad(self.xarm_pos[3:6]), self.haptic_ori)[1]
            target[5] = orientation_transformation(np.deg2rad(self.xarm_pos[3:6]), self.haptic_ori)[2]
        
        else:

            # --- Fixed Orientation ---
            target[3] = self.xarm_pos[3]  
            target[4] = self.xarm_pos[4]  
            target[5] = self.xarm_pos[5]
        
        msg_pos = Float32MultiArray(data=target[0:3])
        msg_ori = Float32MultiArray(data=target[3:6])

        self.pub_pos.publish(msg_pos)
        self.pub_ori.publish(msg_ori)

        self.xarm.set_servo_cartesian(target.tolist(),speed=self.xarm_speed, is_radian=False)

    def send_gripper_command(self):
        omega_gap_m = self.haptic_but 
        gap_mm = omega_gap_m * 1000 * (-1)       
        xarm_cmd = int((gap_mm / 25.0) * 850 - 10)  
        xarm_cmd = np.clip(xarm_cmd, -10, 840)
        self.xarm.set_gripper_position(xarm_cmd, wait=False)

def main():
    rclpy.init()
    node = HapticXArmNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.xarm.set_mode(0)
        node.xarm.set_state(0)
        node.xarm.set_position(x=415, y=0, z=400, roll=180, pitch=0, yaw=-130, speed=80, wait=True)
        node.xarm.disconnect()
        print("Job Finished!")
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
            
if __name__ == '__main__':
    main()

