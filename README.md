
# Base workspace for F1Tenth Platform

## Setup
###  Clone Workspace
    git clone https://github.com/surajkiron/f1tenth_ws.git
    cd f1tenth_ws
    git submodule update --init --recursive 
### Dependencies

Install ros package dependencies using rosdep

    cd F1-TENTH-WORKSPACE-AND-STARTER-CODE
    sudo rosdep init
    rosdep update
    rosdep install --from-paths src/f1tenth_* --ignore-src -r -y

you also will need
    
    sudo apt install ros-${ROS_DISTRO}-asio-cmake-module \
    ros-${ROS_DISTRO}-serial-driver \
    ros-${ROS_DISTRO}-vision-opencv \
    ros-${ROS_DISTRO}-mocap-optitrack

### Connect to Vicon using Mavlink.

1. Start the Vicon Host PC and run **Vicon tracker**
2. Start the **ViconMavlink** software on your **Desktop**
3. Enter the Vicon HostAddress `192.168.1.2`  and select `Menu->Connect Vicon`
4. [Select the object you created](https://www.youtube.com/watch?v=dGMwVMiX7-I) and click `Start a MavLink Sender`
5. Connect to wifi<br>
    **ssid**: ViconRouter_5G<br>
    **password**: ViconRouter<br>
    Enter your laptop ip address in **Remote IP**
    (run `ifconfig` on linux or `ipconfig` on windows and look for `inet 192.168.1.##`)
6. Set the desired frequency and click start

### Preinstalled Dependencies
- [librealsense sdk-v2.56.3](https://github.com/IntelRealSense/librealsense/blob/v2.56.3/doc/installation.md)

# Usage
    ros2 run vicon_control vicon_bridge

    ros2 launch 
