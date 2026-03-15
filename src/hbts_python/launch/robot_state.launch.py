from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # 1. The Publisher Node
    xarm_publisher_node = Node(
        package='hbts_python',
        executable='xarm_state_publisher',
        name='xarm_state_pub',
        output='screen',
    )

    # 2. The Visualizer Node 
    xarm_visualizer_node = Node(
        package='hbts_python',
        executable='topic_visualizer',
        name='xarm_visualizer',
        output='screen',
        parameters=[{'topic': '/xarm_joint_currents'}, {'buffer': 6000}]
    )

    return LaunchDescription([
        xarm_publisher_node,
        xarm_visualizer_node
    ])