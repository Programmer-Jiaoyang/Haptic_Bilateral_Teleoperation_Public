import rclpy
import random
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
import math
import time

class FakeFTSensorPublisher(Node):
    def __init__(self):
        super().__init__('fake_ft_sensor_publisher')
        self.pub = self.create_publisher(Float32MultiArray, '/ft_data_fake', 10)
        self.timer_period = 0.01
        self.timer = self.create_timer(self.timer_period, self.publish_ft)
        self.t_start = time.time()
        self.noise_std =0.5

    def publish_ft(self):
        t = time.time() - self.t_start
        fx = 25*math.sin(2 * math.pi * 0.5 * t) + random.gauss(0, self.noise_std)
        fy = 24*math.cos(2 * math.pi * 0.5 * t) + random.gauss(0, self.noise_std)
        fz = 26*math.sin(2 * math.pi * 0.25 * t) + random.gauss(0, self.noise_std)
        msg = Float32MultiArray(data=[fx, fy, fz])
        self.pub.publish(msg)
        # self.get_logger().info(f'Published: Fx={fx:.2f}, Fy={fy:.2f}, Fz={fz:.2f}')

def main(args=None):
    rclpy.init(args=args)
    node = FakeFTSensorPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()