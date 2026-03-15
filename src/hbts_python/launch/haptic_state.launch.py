from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # 1. The Haptic Node
    haptic_driver_node = Node(
        package='hbts_c',
        executable='haptic_driver',
        name='haptic_driver',
        output='screen',
        parameters=[{'use_haptic': False}]
    )

    # 2. The Visualizer Node 
    haptic_pos_visualizer_node = Node(
        package='hbts_python',
        executable='topic_visualizer',
        name='haptic_visualizer',
        output='screen',
        parameters=[{'topic': '/haptic_position'}, {'buffer': 6000}]
    )
    
    # 3. The Visualizer Node 
    haptic_ori_visualizer_node = Node(
        package='hbts_python',
        executable='topic_visualizer',
        name='haptic_visualizer',
        output='screen',
        parameters=[{'topic': '/haptic_orientation'}, {'buffer': 6000}]
    )


    return LaunchDescription([
        haptic_driver_node,
        haptic_pos_visualizer_node,
        haptic_ori_visualizer_node
    ])