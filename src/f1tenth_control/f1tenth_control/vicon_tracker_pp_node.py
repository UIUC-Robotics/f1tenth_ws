#!/usr/bin/env python3

import os
import csv
import math
import numpy as np
from numpy import linalg as la

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
from ackermann_msgs.msg import AckermannDriveStamped

class PurePursuit(Node):
    def __init__(self):
        super().__init__('vicon_pp_node')

        self.rate_hz = 50
        self.timer_period = 1.0 / self.rate_hz

        self.look_ahead = 0.3  # meters
        self.wheelbase = 0.325  # meters
        self.offset = 0.15  # meters

        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0  # degrees

        # Publisher
        self.ctrl_pub = self.create_publisher(
            AckermannDriveStamped,
            "/drive",
            1
        )

        self.drive_msg = AckermannDriveStamped()
        self.drive_msg.header.frame_id = "f1tenth_control"
        self.drive_msg.drive.speed = 0.0  # m/s, reference speed

        # Subscriber
        self.vicon_sub = self.create_subscription(
            Float64MultiArray,
            '/car_state',
            self.carstate_callback,
            10
        )

        # Read waypoints
        self.goal = 0
        self.read_waypoints()

        # Timer for control loop
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

    def carstate_callback(self, msg: Float64MultiArray):
        self.x = msg.data[0]
        self.y = msg.data[1]
        self.yaw = msg.data[3]
        self.drive_msg.drive.speed = 1.0  # set constant speed only if you have odometry
        # print(f"Received state: x={self.x}, y={self.y}, yaw={self.yaw}")

    def read_waypoints(self):
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, '../waypoints/xyhead_demo_pp.csv')

        with open(filename) as f:
            path_points = [tuple(line) for line in csv.reader(f)]

        self.path_points_x_record = [float(point[0]) for point in path_points]
        self.path_points_y_record = [float(point[1]) for point in path_points]
        self.path_points_yaw_record = [float(point[2]) for point in path_points]
        self.wp_size = len(self.path_points_x_record)
        self.dist_arr = np.zeros(self.wp_size)

    def get_f1tenth_state(self):
        curr_yaw = math.radians(self.yaw)
        curr_x = self.x - self.offset * math.cos(curr_yaw)
        curr_y = self.y - self.offset * math.sin(curr_yaw)

        return round(curr_x, 3), round(curr_y, 3), round(curr_yaw, 4)

    def find_angle(self, v1, v2):
        cosang = np.dot(v1, v2)
        sinang = la.norm(np.cross(v1, v2))
        return np.arctan2(sinang, cosang)

    def dist(self, p1, p2):
        return round(math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2), 3)

    def timer_callback(self):
        path_points_x = np.array(self.path_points_x_record)
        path_points_y = np.array(self.path_points_y_record)

        curr_x, curr_y, curr_yaw = self.get_f1tenth_state()

        # Calculate distances from current position to all waypoints
        for i in range(len(path_points_x)):
            self.dist_arr[i] = self.dist((path_points_x[i], path_points_y[i]), (curr_x, curr_y))

        # Find candidate points within lookahead range ± 0.05 m
        goal_arr = np.where(
            (self.dist_arr < self.look_ahead + 0.15) &
            (self.dist_arr > self.look_ahead - 0.15)
        )[0]

        # Find goal point ahead of the vehicle
        for idx in goal_arr:
            v1 = [path_points_x[idx] - curr_x, path_points_y[idx] - curr_y]
            v2 = [math.cos(curr_yaw), math.sin(curr_yaw)]
            temp_angle = self.find_angle(v1, v2)
            if abs(temp_angle) < math.pi / 2:
                self.goal = idx
                break

        L = self.dist_arr[self.goal]
        alpha = math.radians(self.path_points_yaw_record[self.goal]) - curr_yaw

        # Pure Pursuit control law tuning parameters
        k = 0.4
        angle_i = math.atan((k * 2 * self.wheelbase * math.sin(alpha)) / L)
        angle = angle_i * 2

        f_delta = round(np.clip(angle, -0.3, 0.3), 3)
        f_delta_deg = round(math.degrees(f_delta))

        self.get_logger().info(f"Current index: {self.goal}")
        ct_error = round(math.sin(alpha) * L, 3)
        self.get_logger().info(f"Crosstrack Error: {ct_error}")
        self.get_logger().info(f"Front steering angle: {f_delta_deg} degrees\n")

        self.drive_msg.header.stamp = self.get_clock().now().to_msg()
        self.drive_msg.drive.steering_angle = f_delta

        self.ctrl_pub.publish(self.drive_msg)
        # print("From timer_callback: Published drive message with steering angle:", f_delta_deg)


def main(args=None):
    rclpy.init(args=args)
    pp = PurePursuit()

    try:
        rclpy.spin(pp)
    except KeyboardInterrupt:
        pass

    pp.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
