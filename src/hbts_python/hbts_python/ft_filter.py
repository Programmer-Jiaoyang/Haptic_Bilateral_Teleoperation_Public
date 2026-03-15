import sys
print("Python executable:", sys.executable, flush=True)
print("Python version:", sys.version, flush=True)
print("Version 1.0.0", flush=True)

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray

class FTHapticFilter(Node):
    def __init__(self):
        super().__init__('ft_haptic_filter')
        # --- Declare parameters ---
        self.declare_parameter('topic', '/ft_data')
        self.declare_parameter('alpha', 0.25)
        self.declare_parameter('scale_x', 0.25)
        self.declare_parameter('scale_y', 0.25)
        self.declare_parameter('scale_z', 0.25)
        self.declare_parameter('scale_tx', 0.25)
        self.declare_parameter('scale_ty', 0.25)
        self.declare_parameter('scale_tz', 0.25)
        self.declare_parameter('max_force', 10.0)
        self.declare_parameter('deadband', 0.5)

        # --- Get parameters ---
        self.topic = self.get_parameter('topic').get_parameter_value().string_value
        self.alpha = self.get_parameter('alpha').get_parameter_value().double_value
        self.scale_x = self.get_parameter('scale_x').get_parameter_value().double_value
        self.scale_y = self.get_parameter('scale_y').get_parameter_value().double_value
        self.scale_z = self.get_parameter('scale_z').get_parameter_value().double_value
        self.scale_tx = self.get_parameter('scale_tx').get_parameter_value().double_value
        self.scale_ty = self.get_parameter('scale_ty').get_parameter_value().double_value
        self.scale_tz = self.get_parameter('scale_tz').get_parameter_value().double_value
        self.max_force = self.get_parameter('max_force').get_parameter_value().double_value
        self.deadband = self.get_parameter('deadband').get_parameter_value().double_value

        self.prev = None
        self.scale = [self.scale_x, self.scale_y, self.scale_z,self.scale_tx, self.scale_ty, self.scale_tz]

        self.sub = self.create_subscription(Float32MultiArray,self.topic,self.callback,10)
        self.pub = self.create_publisher(Float32MultiArray,self.topic + "_processed",10)

        self.get_logger().info(f"Input topic: {self.topic}")
        self.get_logger().info(f"Output topic: {self.topic}_processed")
        self.get_logger().info(f"alpha={self.alpha} scale={self.scale} max_force={self.max_force} deadband={self.deadband}")

    def callback(self, msg):
        
        data = list(msg.data)

        # ---------- smoothing ----------
        if self.prev is None:
            self.prev = data
        else:
            for i in range(len(data)):
                self.prev[i] = self.alpha * data[i] + (1 - self.alpha) * self.prev[i]

        filtered = list(self.prev)

        # ---------- deadband ----------
        for i in range(len(filtered)):
            if abs(filtered[i]) < self.deadband:
                filtered[i] = 0.0

        # ---------- scaling ----------
        for i in range(len(filtered)):
            filtered[i] *= self.scale[i]

        # ---------- saturation ----------
        for i in range(len(filtered)):
            if filtered[i] > self.max_force:
                filtered[i] = self.max_force
            elif filtered[i] < -self.max_force:
                filtered[i] = -self.max_force

        out = Float32MultiArray()
        out.data = filtered

        self.pub.publish(out)


def main():
    rclpy.init()
    node = FTHapticFilter()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()