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
  ]
  pure_pursuit_node = Node(
      package='f1tenth_control',
      executable='pure_pursuit_control',
      name='pure_pursuit_control',
      namespace='ego_racecar',
      output='screen',
      emulate_tty=True,
  )

  # Launch Description
  ld = LaunchDescription(launch_args)
  ld.add_action(pure_pursuit_node)
  
  return ld