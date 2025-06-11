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
  ]
  start_cam = LaunchConfiguration("start_cam")
  start_lidar = LaunchConfiguration("start_lidar")
  f1tenth_stack_dir = get_package_share_directory('f1tenth_stack')

  no_lidar_bringup_launch_file = os.path.join(f1tenth_stack_dir, 'launch', 'no_lidar_bringup_launch.py')

  params = os.path.join(get_package_share_directory('f1tenth_control'), 'config', 'camera.yaml')
  _output = 'screen'  # or 'log'
  print("[DEBUG] PARAM PATH:", params)
  realsense_node = Node(
      package='realsense2_camera',
      namespace=LaunchConfiguration('camera_namespace', default=''),
      name=LaunchConfiguration('camera_name', default='D435i'),
      executable='realsense2_camera_node',
      parameters=[os.path.join(
                get_package_share_directory('f1tenth_control'), 'config', 'camera.yaml')],
      output=_output,
      arguments=['--ros-args', '--log-level', LaunchConfiguration('log_level', default='info')],
      emulate_tty=True,
      condition=IfCondition(start_cam),
 )

# Add the node to the launch description
  # Launch Description
  ld = LaunchDescription(launch_args)

  ld.add_action(realsense_node)
  ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [FindPackageShare("f1tenth_stack"), '/launch', '/bringup_launch.py']
            ),
            condition=IfCondition(start_lidar),
        ))
  ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [FindPackageShare("f1tenth_stack"), '/launch', '/no_lidar_bringup_launch.py']
            ),
            condition=UnlessCondition(start_lidar),
        ))
  return ld