
## Mount Batteries
  1. Connect the 12V battery for NVIDIA Jetson NX and LiDAR sensor.

<img src="images/nx_power-2048x1287.png" alt="System overview"      style="display:block; margin:0 auto; width:60%; height:auto;">

    2. Connect the 11.1V Lipo battery for F1TENTH car and VESC

<img src="images/vesc_power-2048x1392.png" alt="System overview"      style="display:block; margin:0 auto; width:60%; height:auto;">

    3. The NVIDIA Jetson computer will boot automatically. Put the F1TENTH car on the ground and go to Host Computer Setup

<img src="images/Weixin-Image_20231017223129-2048x1536.jpg" alt="System overview"      style="display:block; margin:0 auto; width:60%; height:auto;"> 


<img src="images/flying_arena.jpg" alt="System overview"      style="display:block; margin:0 auto; width:60%; height:auto;">


<img src="images/vicon_cameras-1536x585.png" alt="System overview"      style="display:block; margin:0 auto; width:60%; height:auto;">


## Motion Capture Setup

### Vicon System

    1. Login the lab computer with your university netid and password.
    2. Power on Vicon (you will hear fans spinning up) and open Vicon Tracker (cameras will boot up) on the desktop.
    3. Choose the objects, namely car#.
<img src="images/vicon_traker_f1tenth-1536x917.png" alt="System overview"      style="display:block; margin:0 auto; width:60%; height:auto;">

    4. Now, you should be able to see the F1tenth car in Vicon Tracker. Next, we need to publish the information, such as positions and orientations of car, to a shared router in real time. Then, a ROS node would be launched on the Jetson on the F1TENTH car to receive the those messages. In this way, the VICON system acts as the “indoor GPS” system.

    5. Subscribe to position data using the motion capture tracking package. In your workspace launch the motion capture node. 
```
cd your_ws
source install/setup.bash
ros2 launch motion_capture_tracking launch_3d_pose_publisher.py

# check to see if you're getting odometry data
ros2 topic echo /car#/odom
```

>[!NOTE]
> You don't need to launch this with pure_pursuit.launch.py because it will start the node by default.

### Optitrack System

modify the [config](https://github.com/UIUC-Robotics/motion_capture_tracking/blob/ros2/motion_capture_tracking/config/cfg.yaml)

`type: optitrack`  
`hostname: 192.168.50.146`


## PC Setup
 1. Connect your personal laptop to lab’s route.  
    Wifi Name: ViconRouter5G  or ViconRouter2.4G  
    Wifi Password: ViconRouter

 2. Use [VNC viewer](https://developer.nvidia.com/embedded/learn/tutorials/vnc-setup) software to connect NVIDIA Jetson computer remotely.  
    Open RealVNC Viewer, choose File -> New connection
 VNC viewer is also available on the Vicon System

 3. Alternatively use ssh (preferred)
 ```
 ssh -X orin@192.168.1.171
 
 # if you don't need GUI you can disable X11 forwarding

 ssh orin@192.168.1.171
 ```
 4. If you have ubuntu22 or can run it on a docker container or have ros2 for Windows. You can subscribe to ros2 topics on your PC. You can run visualization by running this (image stream will still be slow).  
 Make sure your ROS_DOMAIN_ID is the same as the car.
 > [!NOTE] See the [f1tenth_simulator]() repo for ubuntu22 docker image.
 ```
 # On the car, check DOMAIN ID
 echo $ROS_DOMAIN_ID
 # or 
 printenv | grep ROS

 # On remote PC
 export ROS_DOMAIN_ID=51
 # check topics if nodes are up and running on car
 ros2 topic list
 ros2 launch f1tenth_control visualization_launch.py
 ```
 <img src="images/racecar_rviz-1536x789.png" alt="System overview"      style="display:block; margin:0 auto; width:60%; height:auto;">


## To Launch pure pursuit demo
```
cd your_ws
source install/setup.bash
ros2 launch f1tenth_control pure_pursuit.launch.py car_name:=car#
```
