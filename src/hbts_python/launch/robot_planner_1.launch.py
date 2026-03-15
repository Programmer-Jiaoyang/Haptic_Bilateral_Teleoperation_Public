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

    # 2. The Xarm Node 
    xarm_planner_node = Node(
        package='hbts_python',
        executable='xarm_motion_planner_1',
        name='xarm_planner',
        output='screen',
    )
    # 3. The Keyboard Node 
    keyboard_node = Node(
        package='hbts_python',
        executable='keyboard_publisher',
        name='keyboard_publisher',
        output='screen',
    )
    
    # 4. The Visualizer Node 
    xarm_pos_visualizer_node = Node(
        package='hbts_python',
        executable='topic_visualizer',
        name='xarm_goal_position_visualizer',
        output='screen',
        parameters=[{'topic': '/xarm_goal_position'}, {'buffer': 600}]
    )

    # 5. The Visualizer Node 
    xarm_ori_visualizer_node = Node(
        package='hbts_python',
        executable='topic_visualizer',
        name='xarm_goal_orientation_visualizer',
        output='screen',
        parameters=[{'topic': '/xarm_goal_orientation'}, {'buffer': 600}]
    )
    return LaunchDescription([
        haptic_driver_node,
        xarm_planner_node,
        keyboard_node,
        xarm_pos_visualizer_node,
        xarm_ori_visualizer_node
    ])