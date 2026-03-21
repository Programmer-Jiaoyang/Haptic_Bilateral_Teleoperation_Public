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
    
    # 2. The Filter Node 
    ft_filter_node = Node(
        package='hbts_python',
        executable='ft_filter',
        name='ft_filter',
        output='screen',
        parameters=[{'topic': '/ft_data'}, {'scale_z': 0.4}]
    )

    # 3. The Haptic Node
    haptic_driver_node = Node(
        package='hbts_c',
        executable='haptic_driver',
        name='haptic_driver',
        output='screen',
        parameters=[{'use_haptic': True}]
    )
    
    # 4. The Visualizer Node 2
    ft_visualizer_node = Node(
        package='hbts_python',
        executable='topic_visualizer',
        name='haptic_visualizer',
        output='screen',
        parameters=[{'topic': '/haptic_rendering_force'}, {'buffer': 5000}]
    )

    # 5. The Xarm Node 
    xarm_planner_node = Node(
        package='hbts_python',
        executable='xarm_motion_planner_2',
        name='xarm_planner',
        output='screen',
        parameters=[{'use_orientation': False}]
    )
    
    # 6. The Keyboard Node 
    keyboard_node = Node(
        package='hbts_python',
        executable='keyboard_publisher',
        name='keyboard_publisher',
        output='screen',
    )

    return LaunchDescription([
        ft_publisher_node,
        ft_filter_node,
        haptic_driver_node,
        ft_visualizer_node,
        xarm_planner_node,
        keyboard_node,
    ])