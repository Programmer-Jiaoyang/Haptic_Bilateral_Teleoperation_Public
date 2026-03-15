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

    # 2. The Visualizer Node 1
    ft_visualizer_node_1 = Node(
        package='hbts_python',
        executable='topic_visualizer',
        name='ft_visualizer',
        output='screen',
        parameters=[{'topic': '/ft_data'}, {'buffer': 500}]
    )

    # 3. The Filter Node 
    ft_filter_node = Node(
        package='hbts_python',
        executable='ft_filter',
        name='ft_filter',
        output='screen',
        parameters=[{'topic': '/ft_data'}]
    )
    
    # 4. The Haptic Node 
    haptic_node = Node(
        package='hbts_c',
        executable='haptic_driver',
        name='haptic_device',
        output='screen',
        parameters=[{'use_haptic': True}]
    )

    # 5. The Visualizer Node 2
    ft_visualizer_node_2 = Node(
        package='hbts_python',
        executable='topic_visualizer',
        name='haptic_visualizer',
        output='screen',
        parameters=[{'topic': '/haptic_rendering_force'}, {'buffer': 5000}]
    )
    return LaunchDescription([
        ft_publisher_node,
        ft_visualizer_node_1,
        ft_filter_node,
        ft_visualizer_node_2,
        haptic_node,
    ])