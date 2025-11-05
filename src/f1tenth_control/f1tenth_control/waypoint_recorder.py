#!/usr/bin/env python3

import os
import csv
import math

import rclpy
from rclpy.node import Node
from tf_transformations import euler_from_quaternion
from nav_msgs.msg import Odometry
from std_srvs.srv import Trigger


class WaypointRecorder(Node):
    def __init__(self):
        super().__init__('waypoint_recorder')

        # Parameters
        self.declare_parameter('recording_frequency', 10.0)  # Hz
        self.declare_parameter('distance_threshold', 0.02)  # meters - minimum distance between waypoints
        self.declare_parameter('output_filename', 'recorded_waypoints.csv')
        self.declare_parameter('auto_start', True)  # Automatically start recording on launch
        
        self.recording_freq = self.get_parameter('recording_frequency').value
        self.dist_threshold = self.get_parameter('distance_threshold').value
        self.output_filename = self.get_parameter('output_filename').value
        self.auto_start = self.get_parameter('auto_start').value

        # State variables
        self.is_recording = self.auto_start
        self.waypoints = []
        self.last_x = None
        self.last_y = None
        self.last_yaw = None

        # Current position
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0

        # Subscriber to odometry
        self.odom_sub = self.create_subscription(
            Odometry,
            '/car3/odom',
            self.odom_callback,
            10
        )

        # Services to start/stop recording
        self.start_service = self.create_service(
            Trigger,
            'start_recording',
            self.start_recording_callback
        )
        self.stop_service = self.create_service(
            Trigger,
            'stop_recording',
            self.stop_recording_callback
        )

        # Timer for recording waypoints at fixed frequency
        self.timer_period = 1.0 / self.recording_freq
        self.record_timer = self.create_timer(self.timer_period, self.record_waypoint)
        
        # Timer for periodic status updates (every 5 seconds)
        self.status_timer = self.create_timer(5.0, self.status_update)

        self.get_logger().info('Waypoint Recorder Node Started')
        self.get_logger().info('Subscribed to: /car3/odom')
        self.get_logger().info(f'Recording frequency: {self.recording_freq} Hz')
        self.get_logger().info(f'Distance threshold: {self.dist_threshold} m')
        self.get_logger().info(f'Output file: {self.output_filename}')
        
        if self.is_recording:
            self.get_logger().info('*** RECORDING STARTED AUTOMATICALLY ***')
            self.get_logger().info('*** Press Ctrl-C to stop and save waypoints ***')
        else:
            self.get_logger().info('Use "ros2 service call /start_recording std_srvs/srv/Trigger" to start recording')
            self.get_logger().info('Use "ros2 service call /stop_recording std_srvs/srv/Trigger" to stop and save')

    def odom_callback(self, msg: Odometry):
        """Callback to update current position from odometry"""
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        
        q = msg.pose.pose.orientation
        _, _, self.yaw = euler_from_quaternion([q.x, q.y, q.z, q.w])

    def status_update(self):
        """Periodic status update to show recording progress"""
        if self.is_recording:
            self.get_logger().info(f'Recording... {len(self.waypoints)} waypoints collected | '
                                 f'Current position: ({self.x:.3f}, {self.y:.3f})')

    def start_recording_callback(self, _request, response):
        """Service callback to start recording waypoints"""
        if self.is_recording:
            response.success = False
            response.message = 'Already recording waypoints'
        else:
            self.is_recording = True
            self.waypoints = []
            self.last_x = None
            self.last_y = None
            self.last_yaw = None
            response.success = True
            response.message = 'Started recording waypoints'
            self.get_logger().info('Recording started')
        
        return response

    def stop_recording_callback(self, _request, response):
        """Service callback to stop recording and save waypoints"""
        if not self.is_recording:
            response.success = False
            response.message = 'Not currently recording'
        else:
            self.is_recording = False
            
            if len(self.waypoints) > 0:
                success = self.save_waypoints()
                if success:
                    response.success = True
                    response.message = f'Stopped recording. Saved {len(self.waypoints)} waypoints to {self.output_filename}'
                    self.get_logger().info(f'Recording stopped. Saved {len(self.waypoints)} waypoints')
                else:
                    response.success = False
                    response.message = 'Failed to save waypoints'
            else:
                response.success = False
                response.message = 'No waypoints recorded'
                self.get_logger().warn('Recording stopped but no waypoints were recorded')
        
        return response

    def record_waypoint(self):
        """Timer callback to record waypoints at fixed frequency"""
        if not self.is_recording:
            return

        # Check if we've moved enough from last waypoint
        if self.last_x is not None and self.last_y is not None:
            distance = math.sqrt((self.x - self.last_x)**2 + (self.y - self.last_y)**2)
            if distance < self.dist_threshold:
                return  # Don't record if we haven't moved enough

        # Convert yaw from radians to degrees
        yaw_deg = round(math.degrees(self.yaw))
        
        # Normalize to -180 to 180 range
        if yaw_deg > 180:
            yaw_deg -= 360
        elif yaw_deg < -180:
            yaw_deg += 360

        # Record waypoint
        waypoint = {
            'x': round(self.x, 3),
            'y': round(self.y, 3),
            'yaw': yaw_deg
        }
        
        self.waypoints.append(waypoint)
        self.last_x = self.x
        self.last_y = self.y
        self.last_yaw = self.yaw

        self.get_logger().debug(f'Recorded waypoint #{len(self.waypoints)}: x={waypoint["x"]}, y={waypoint["y"]}, yaw={waypoint["yaw"]}')

    def save_waypoints(self):
        """Save recorded waypoints to CSV file"""
        try:
            # Get the waypoints directory path
            dirname = os.path.dirname(__file__)
            waypoints_dir = os.path.join(dirname, '../waypoints')
            
            # Create directory if it doesn't exist
            os.makedirs(waypoints_dir, exist_ok=True)
            
            # Full path to output file
            filepath = os.path.join(waypoints_dir, self.output_filename)
            
            # Write to CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                for wp in self.waypoints:
                    writer.writerow([wp['x'], wp['y'], wp['yaw']])
            
            self.get_logger().info(f'Waypoints saved to: {filepath}')
            return True
            
        except (OSError, IOError) as e:
            self.get_logger().error(f'Error saving waypoints: {str(e)}')
            return False


def main(args=None):
    rclpy.init(args=args)
    recorder = WaypointRecorder()

    try:
        rclpy.spin(recorder)
    except KeyboardInterrupt:
        recorder.get_logger().info('\n*** Ctrl-C detected! ***')
    finally:
        # Save waypoints on shutdown if recording or if waypoints were recorded
        if len(recorder.waypoints) > 0:
            recorder.get_logger().info(f'Saving {len(recorder.waypoints)} waypoints...')
            if recorder.save_waypoints():
                recorder.get_logger().info('Waypoints saved successfully!')
            else:
                recorder.get_logger().error('Failed to save waypoints!')
        else:
            recorder.get_logger().warn('No waypoints recorded')

        recorder.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

