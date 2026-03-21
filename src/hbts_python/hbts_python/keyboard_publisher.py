import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from pynput import keyboard

class SpeedPublisher(Node):
    def __init__(self):
        super().__init__('speed_publisher')

        # Publisher
        self.publisher_ = self.create_publisher(Float32, '/speed', 10)

        # Speed settings
        self.speed = 30.0
        self.min_speed = 10.0
        self.max_speed = 200.0
        self.speed_step = 10.0

        self.get_logger().info("Speed publisher started")
        self.get_logger().info("Default speed is: 30 mm/s")
        self.get_logger().info("Press 'w' to increase speed, 's' to decrease speed")

        # Start keyboard listener
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

        # Timer to publish speed periodically
        self.create_timer(0.25, self.publish_speed)

    def on_press(self, key):
        """Update speed when 'w' or 's' is pressed."""
        try:
            if key.char == 'w':
                self.speed = min(self.speed + self.speed_step, self.max_speed)
                self.get_logger().info(f"Speed increased: {self.speed}")
            elif key.char == 's':
                self.speed = max(self.speed - self.speed_step, self.min_speed)
                self.get_logger().info(f"Speed decreased: {self.speed}")
        except AttributeError:
            # Ignore special keys
            pass

    def publish_speed(self):
        """Publish the current speed."""
        msg = Float32()
        msg.data = self.speed
        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = SpeedPublisher()

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