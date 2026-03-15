import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'hbts_python'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='jiaoyangl',
    maintainer_email='jiaoyangl@todo.todo',
    description='TODO: Package description',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        'ft_fake_node = hbts_python.ft_fake_node:main',
        'ft_filter = hbts_python.ft_filter:main',
        'ft_publisher = hbts_python.ft_publisher:main',
        'xarm_state_publisher = hbts_python.xarm_state_publisher:main',
        'xarm_motion_planner_1 = hbts_python.xarm_motion_planner_1:main',
        'xarm_motion_planner_2 = hbts_python.xarm_motion_planner_2:main',
        'topic_visualizer = hbts_python.topic_visualizer:main',
        'keyboard_publisher = hbts_python.keyboard_publisher:main',
        ],
    },
)
