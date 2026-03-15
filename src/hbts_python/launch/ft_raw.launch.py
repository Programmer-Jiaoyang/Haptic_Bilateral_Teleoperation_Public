from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # 1. The Publisher Node
    ft_publisher_node = Node(
        package='hbts_python',
        executable='ft_publisher',
        name='ft_sensor_pub',
        output='screen',
        parameters=[{'portname': '/dev/ttyUSB0'}]
    )

    # 2. The Visualizer Node 
    ft_visualizer_node = Node(
        package='hbts_python',
        executable='topic_visualizer',
        name='ft_visualizer',
        output='screen',
        parameters=[{'topic': '/ft_data'}, {'buffer': 500}]
    )

    return LaunchDescription([
        ft_publisher_node,
        ft_visualizer_node
    ])