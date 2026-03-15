"""
ROS2 Node: Haptic to XArm
Subscribes to haptic device pose, processes it, and moves the robot in real-time.
Mapping strategy: absolute mapping
Control strategy: arm.set_position
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
from std_msgs.msg import Float32MultiArray,Bool, Float32
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

class HapticXArmNode(Node):
    def __init__(self):
        super().__init__('haptic_to_xarm_node')
        # Latest haptic data
        self.haptic_pos = np.zeros(3)
        self.haptic_ori = np.zeros(3)

        # Scale & offset
        self.scale = np.array([1, 1, 1])
        self.offset = np.array([0.415, 0, 0.2])

        # Default speed and pose
        self.xarm_speed = 50
        self.xarm_pos = [415, 0, 200, -180, 0, -130]
        
        # Motion smoother
        # self.pos_filter = LowPassFilter(alpha=0.25)

        # Ros Args
        self.declare_parameter('position_topic', '/haptic_position')
        self.declare_parameter('orientation_topic', '/haptic_orientation')
        self.declare_parameter('button_topic', '/haptic_button')
        self.declare_parameter('xarm_ip', '192.168.1.245')

        self.position_topic = self.get_parameter('position_topic').get_parameter_value().string_value
        self.orientation_topic = self.get_parameter('orientation_topic').get_parameter_value().string_value
        self.button_topic = self.get_parameter('button_topic').get_parameter_value().string_value
        self.xarm_ip = self.get_parameter('xarm_ip').get_parameter_value().string_value
        
        # Connect robot
        self.xarm = XArmAPI(self.xarm_ip)
        self.init_robot()

        # Subscriber to haptic topic
        self.sub_pos = self.create_subscription(Float32MultiArray, self.position_topic, self.pos_cb, 10)
        self.sub_ori = self.create_subscription(Float32MultiArray, self.orientation_topic, self.ori_cb, 10)
        self.sub_btn = self.create_subscription(Bool, self.button_topic, self.button_cb, 10)
        self.sub_vel = self.create_subscription(Float32, "/speed", self.speed_cb, 10)
        
        # Publisher target pose
        self.pub_pos = self.create_publisher(Float32MultiArray, '/xarm_goal_position', 10)
        self.pub_ori = self.create_publisher(Float32MultiArray, '/xarm_goal_orientation', 10)

        # Timer to send robot commands at 100 Hz
        self.create_timer(0.01, self.send_robot_command)  

    def init_robot(self):
        self.xarm.motion_enable(True)
        self.xarm.set_mode(0)
        self.xarm.set_state(0)
        self.xarm.set_position(x=self.xarm_pos[0], y=self.xarm_pos[1], z=self.xarm_pos[2]+50, roll=self.xarm_pos[3], pitch=self.xarm_pos[4], yaw=self.xarm_pos[5], speed=30, wait=True)
        self.xarm.set_position(x=self.xarm_pos[0], y=self.xarm_pos[1], z=self.xarm_pos[2], roll=self.xarm_pos[3], pitch=self.xarm_pos[4], yaw=self.xarm_pos[5], speed=30, wait=True)
        self.get_logger().info("XArm initialized. Set mode to 0")
        time.sleep(1)

    def pos_cb(self, msg):
        self.haptic_pos = np.array(msg.data[:3])
        # self.haptic_pos = self.pos_filter.filter(msg.data[:3])

    def ori_cb(self, msg):
        self.haptic_ori = np.array(msg.data[:3])

    def button_cb(self, msg):
        return
        # if msg.data:
        #     self.get_logger().info("Button pressed, stopping node")
        #     rclpy.shutdown()

    def speed_cb(self, msg):
        self.xarm_speed = float(msg.data)

    def send_robot_command(self):
        target = np.zeros(6)
        target[0:3] = (self.haptic_pos + self.offset) * 1000 *self.scale
        
        # # --- Orientation mapping (XYZ to ZYX) ---
        # a = self.haptic_ori  
        # r = R.from_euler('xyz', a)          
        # c = r.as_euler('zyx')
        
        target[3] = self.xarm_pos[3] 
        target[4] = self.xarm_pos[4]  
        target[5] = self.xarm_pos[5] 

        # target[3] = np.rad2deg(c[2])  
        # target[4] = np.rad2deg(c[1])  
        # target[5] = np.rad2deg(c[0]) 
        
        msg_pos = Float32MultiArray(data=target[0:3])
        msg_ori = Float32MultiArray(data=target[3:6])

        self.pub_pos.publish(msg_pos)
        self.pub_ori.publish(msg_ori)

        self.xarm.set_position(x= target[0], y=target[1], z=target[2], roll=target[3], pitch=target[4], yaw=target[5], speed = self.xarm_speed, wait=True)

def main():
    rclpy.init()
    node = HapticXArmNode()

    rclpy.spin(node)
    node.xarm.reset(True)
    node.xarm.disconnect()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
