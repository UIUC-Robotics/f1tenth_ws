from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription, DeclareLaunchArgument
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import LaunchConfiguration, TextSubstitution, EnvironmentVariable, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.conditions import IfCondition, UnlessCondition
from ament_index_python.packages import get_package_share_directory
import os
from launch_ros.actions import Node
from launch_ros.actions import PushRosNamespace

def generate_launch_description():
  launch_args = [
        DeclareLaunchArgument(name="car_name", default_value="car3", description="car name"),
        DeclareLaunchArgument(name="start_cam", default_value="false", description="Start realsense camera"),
        DeclareLaunchArgument(name="start_lidar", default_value="false", description="Start Hokuyo lidar"),
        DeclareLaunchArgument(name="start_visualization", default_value="false", description="Start rviz visualization"),
  ]
  car_name = LaunchConfiguration("car_name")
  start_cam = LaunchConfiguration("start_cam")
  start_lidar = LaunchConfiguration("start_lidar")
  start_visualization = LaunchConfiguration("start_visualization")
  sensors_config = os.path.join(
        get_package_share_directory('f1tenth_control'),
        'config',
        'sensors.yaml'
    )
  params = os.path.join(get_package_share_directory('f1tenth_control'), 'config', 'joy_teleop.yaml')
  mocap_config = os.path.join(
        get_package_share_directory('motion_capture_tracking'),
        'config',
        'cfg.yaml')
  print("[DEBUG] PARAM PATH:", params)
  mocap_node = Node(
        package='motion_capture_tracking',
        executable='3d_pose_motion_capture_node',
        name='motion_capture_tracking',
        output='screen',
        parameters=[mocap_config],
  )
  pure_pursuit_node = Node(
      package='f1tenth_control',
      executable='pure_pursuit_control',
      name='pure_pursuit_control',
      namespace='',
      output='screen',
      emulate_tty=True,
      remappings=[
        ('/odom', [car_name, '/odom'])
        ],
  )
  static_transform_node = Node(
      package='tf2_ros',
      executable='static_transform_publisher',
      name='world_to_map',
      arguments=[
          '0.08875938504934311',
          '-0.3511563539505005',
          '-0.004507781006395817',
          '0.013775953091681004',
          '-0.005556662101298571',
          '0.9736091494560242',
          '-0.22773799300193787',
          'world',
          'map'
      ],
      output='screen'
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
  ld.add_action(mocap_node)
  ld.add_action(urg_node)
  ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [FindPackageShare("f1tenth_control"), '/launch', '/teleop.launch.py']
            ),
        ))
  ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [FindPackageShare("f1tenth_control"), '/launch', '/visualization_launch.py']
            ),
            condition=IfCondition(start_visualization),
        ))
  ld.add_action(pure_pursuit_node)
  ld.add_action(static_transform_node)
  return ld