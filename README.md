### Project Description

This demo shows how to build a haptic bilateral teleoperation system with **Ufactory xArm6**, **Robotiq FT-300** sensor and **Force Dimension Omega.7** haptic device. The demo is implemented and tested in following environment:

**System:** Ubuntu 22.04.4 LTS

**ROS2:** Humble

**Python:** 3.9.13

Currently, the demo only shows the teleoperation in X,Y,Z directions. The orientation of the slave robot is kept as fixed.



### Demo Description

Run the following launch files to try the demos:

```
ros2 launch hbts_python ft_raw.launch.py
```

A demo that tests the **FT sensor**. The raw FT sensor data is visualized.

```
ros2 launch hbts_python ft_filter.launch.py
```

A demo that tests the **processing of raw FT data**. Both raw and filtered FT sensor data are visualized.

```
ros2 launch hbts_python ft_render.launch.py
```

 A demo that tests the **force rending function of the haptic device** without using robotic arm. The haptic device renders the force information published by the FT sensor. Both the raw and haptic rendering force are visualized.

```
ros2 launch hbts_python robot_state.launch.py
```

 A demo that tests the **robot IP configuration and its connection to the  PC**. The joint currents of the robot are visualized. 

```
ros2 launch hbts_python haptic_state.launch.py
```

 A demo that tests the **haptic device connection  to the  PC**. The pose of the haptic device is visualized.

```
ros2 launch hbts_python robot_planner_1.launch.py
```

 A demo that tests the **robot planner 1**, which uses **arm.set_position()**. The robot receives the motion commands computed from the pose of the haptic device. Haptic rendering is not applied. The keyboard can be used to adjust the robot's motion speed. The goal position and orientation of the robot are visualized.

```
ros2 launch hbts_python robot_planner_2.launch.py
```

 A demo that tests **robot planner 2**, which uses **arm.set_servo_cartesian()**. Other settings are the same as in the previous launch file.

```
ros2 launch hbts_python hbts_demo.launch.py 
```

A demo that demonstrates  the **force rendering function** and **master-slave motion** **between the haptic device and robotic arm** using planner 2. The demo is configured to secure the safe **interaction with the pillow**.



### Release Description

Version 0.0.1

- Initial demo files

Version 0.0.2

- Added support for setting different scale factors for haptic rendering in each direction (**Fx, Fy, Fz, Tx, Ty, Tz**).
- Expanded project documentation.

Version 0.0.3

- Minor refinements to README.md.

Version 0.0.4

- Add Github pages for the project.





