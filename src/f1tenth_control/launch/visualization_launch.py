from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
import os
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'rviz_config',
            default_value=os.path.join(get_package_share_directory('f1tenth_control'), 'rviz', 'f1tenth.rviz'),
            description='Path to the RViz config file'
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', LaunchConfiguration('rviz_config')],
            output='screen'
        )
    ])