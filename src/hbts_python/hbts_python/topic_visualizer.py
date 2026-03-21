import sys
print("Python executable:", sys.executable, flush=True)
print("Python version:", sys.version, flush=True)
print("Version 1.0.2", flush=True)

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, Float64, Float32MultiArray, Float64MultiArray
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

# Map string to ROS2 message type
MSG_TYPES = {
    'Float32': Float32,
    'Float64': Float64,
    'Float32MultiArray': Float32MultiArray,
    'Float64MultiArray': Float64MultiArray,
}

class RealTimePlotter(Node):
    def __init__(self):
        super().__init__('real_time_plotter')

        # ROS2 parameters
        self.declare_parameter('topic', '/ft_data')
        self.declare_parameter('type', 'Float32MultiArray')
        self.declare_parameter('buffer', 100)

        self.topic_name = self.get_parameter('topic').get_parameter_value().string_value
        msg_type_str = self.get_parameter('type').get_parameter_value().string_value
        self.buffer_size = self.get_parameter('buffer').get_parameter_value().integer_value

        # Map string to ROS2 message class
        if msg_type_str not in MSG_TYPES:
            self.get_logger().error(f"Invalid message type '{msg_type_str}', using Float32MultiArray")
            msg_type = Float32MultiArray
        else:
            msg_type = MSG_TYPES[msg_type_str]

        # Data buffer
        self.data_buffer = []
        self.dim = None

        # Subscription
        self.subscription = self.create_subscription(
            msg_type,
            self.topic_name,
            self.callback,
            10
        )

        # Matplotlib setup
        self.fig, self.ax = plt.subplots()
        self.lines = []
        self.ax.set_title(f"Real-time data from '{self.topic_name}'")
        self.ax.set_xlabel("Samples")
        self.ax.set_ylabel("Value")
        self.ax.grid(True)
        self.ani = animation.FuncAnimation(self.fig, self.update_plot, interval=50)

    def callback(self, msg):
        # Extract data
        value = msg.data if hasattr(msg, 'data') else [float(msg)]
        if isinstance(value, (float, int)):
            value = [value]

        # Initialize lines
        if self.dim is None:
            self.dim = len(value)
            for i in range(self.dim):
                line, = self.ax.plot([], [], label=f"Dim {i}")
                self.lines.append(line)
            self.ax.legend(loc='upper right')

        # Append data
        self.data_buffer.append(value)
        if len(self.data_buffer) > self.buffer_size:
            self.data_buffer.pop(0)

    def update_plot(self, frame):
        if not self.data_buffer:
            return
        data_array = np.array(self.data_buffer)
        x = np.arange(len(data_array))
        for i, line in enumerate(self.lines):
            line.set_data(x, data_array[:, i])
        self.ax.relim()
        self.ax.autoscale_view()


def main(args=None):
    rclpy.init(args=args)
    node = RealTimePlotter()

    try:
        while rclpy.ok() and plt.fignum_exists(node.fig.number):
            rclpy.spin_once(node, timeout_sec=0)
            plt.pause(0.001)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass

    finally:
        plt.close('all')
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()



if __name__ == "__main__":
    main()