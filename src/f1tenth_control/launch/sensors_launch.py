from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription, DeclareLaunchArgument
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import LaunchConfiguration, TextSubstitution, EnvironmentVariable, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.conditions import IfCondition, UnlessCondition
from ament_index_python.packages import get_package_share_directory
import os
from launch_ros.actions import Node

def generate_launch_description():
  launch_args = [
        DeclareLaunchArgument(name="start_cam", default_value="true", description="Start realsense camera"),
        DeclareLaunchArgument(name="start_lidar", default_value="true", description="Start Hokuyo lidar"),
        DeclareLaunchArgument(name="start_visualization", default_value="false", description="Start rviz visualization"),
  ]
  start_cam = LaunchConfiguration("start_cam")
  start_lidar = LaunchConfiguration("start_lidar")
  start_visualization = LaunchConfiguration("start_visualization")

  sensors_config = os.path.join(
        get_package_share_directory('f1tenth_control'),
        'config',
        'sensors.yaml'
    )

  params = os.path.join(get_package_share_directory('f1tenth_control'), 'config', 'joy_teleop.yaml')
  print("[DEBUG] PARAM PATH:", params)
  realsense_node = Node(
      package='realsense2_camera',
      namespace=LaunchConfiguration('camera_namespace', default=''),
      name=LaunchConfiguration('camera_name', default='D435i'),
      executable='realsense2_camera_node',
      parameters=[os.path.join(
                get_package_share_directory('f1tenth_control'), 'config', 'camera.yaml')],
      output='screen',
      arguments=['--ros-args', '--log-level', LaunchConfiguration('log_level', default='info')],
      emulate_tty=True,
      condition=IfCondition(start_cam),
  )
  vicon_bridge_node = Node(
      package='f1tenth_control',
      executable='vicon_bridge',
      name='vicon_bridge',
      output='screen',
      parameters=[],
      emulate_tty=True,
  )
  vicon_tracker_node = Node(
      package='f1tenth_control',
      executable='vicon_tracker',
      name='vicon_tracker',
      output='screen',
      emulate_tty=True,
  )
  urg_node = Node(
      package='urg_node',
      executable='urg_node_driver',
      name='urg_node',
      parameters=[sensors_config],
      output='screen',
      condition=IfCondition(start_lidar),
  )


  # Launch Description
  ld = LaunchDescription(launch_args)

  ld.add_action(realsense_node)
  ld.add_action(urg_node)
  ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [FindPackageShare("f1tenth_control"), '/launch', '/visualization_launch.py']
            ),
            condition=IfCondition(start_visualization),
        ))
  return ld


