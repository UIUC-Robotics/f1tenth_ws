## Setup and Installation

### Setup Workspace

    extract ~/f1tenth_ws.tar.gz and rename.

    # or for latest updates

    git clone https://github.com/UIUC-Robotics/f1tenth_ws.git --recursive

    # or

    git clone https://github.com/UIUC-Robotics/f1tenth_ws.git
    cd f1tenth_ws
    git submodule update --init --recursive

### Build your ROS2 workspace

    cd f1tenth_ws;
    colcon build --symlink-install

### Run PurePursuit example code

```
# This will launch Joy Teleop + motion capture system 
ros2 launch f1tenth_control pure_pursuit.launch.py car_name:=car#
```

Now you should be able to control the car using the joy teleop.

### To connect to Vicon using Motion Capture Tracking Package

```
ros2 launch motion_capture_tracking launch_3d_pose_publisher.py 
```

### To launch teleop alone

    ros2 launch f1tenth_control teleop.launch.py
    
### To launch sensors

    # Starts all sensors without rviz visualization
    ros2 launch f1tenth_control sensors_launch.py
    # or
    ros2 launch f1tenth_control sensors_launch.py start_cam:=true start_lidar:=true
    # You can get visualization by running
    ros2 launch f1tenth_control sensors_launch.py start_visualization:=true

### To connect your PC to the car using ros2.
Set the domain id on your PC and the robot. The ROS_DOMAIN_ID ensures that ROS2 topics on the same network don't cross communicate.

```
export ROS_DOMAIN_ID=51 # car1
export ROS_DOMAIN_ID=52 # car2
export ROS_DOMAIN_ID=53 # car3
```

you can check your ROS_DOMAIN_ID by running
```
echo $ROS_DOMAIN_ID
```
### Dependencies

These are already setup for you

- [librealsense sdk-v2.56.3](https://github.com/IntelRealSense/librealsense/blob/v2.56.3/doc/installation.md)

To install ros package dependencies using rosdep

    cd f1tenth_ws
    sudo rosdep init
    rosdep update
    rosdep install --from-paths src/f1tenth_* --ignore-src -r

you also will need

    sudo apt install ros-${ROS_DISTRO}-asio-cmake-module
    ros-${ROS_DISTRO}-serial-driver
    ros-${ROS_DISTRO}-vision-opencv
