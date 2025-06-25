#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
from pymavlink import mavutil
import numpy as np
import time


def pi_2_pi(angle):
    """Convert angle to range [-pi, pi]"""
    if angle > np.pi:
        return angle - 2.0 * np.pi
    if angle < -np.pi:
        return angle + 2.0 * np.pi
    return angle


class ViconBridgeNode(Node):

    def __init__(self):
        super().__init__('vicon_bridge')

        # Publishers
        self.pub_estimate = self.create_publisher(Float64MultiArray, '/vicon_estimate', 10)
        self.pub_path = self.create_publisher(Float64MultiArray, '/car_state', 10)

        # MAVLink connection
        self.master = mavutil.mavlink_connection('udpin:0.0.0.0:10086')

        # Data arrays
        self.data = Float64MultiArray()
        self.data.data = [0.0] * (9 + 2 + 4 + 1)

        self.data_path = Float64MultiArray()
        self.data_path.data = [0.0] * 4

        # Timer at 50Hz
        self.timer = self.create_timer(0.02, self.timer_callback)

    def timer_callback(self):
        msg = self.master.recv_match(blocking=False)
        if not msg:
            return

        if msg.get_type() == 'LOCAL_POSITION_NED_COV':
            self.data.data[0] = msg.x / 1000.
            self.data.data[1] = msg.y / 1000.
            self.data.data[2] = msg.z / 1000.
            self.data.data[3] = msg.vx / 1000.
            self.data.data[4] = msg.vy / 1000.
            self.data.data[5] = msg.vz / 1000.
            self.data.data[6] = msg.ax / 1000.
            self.data.data[7] = msg.ay / 1000.
            self.data.data[8] = msg.az / 1000.

            offset = 100.0
            self.data.data[9]  = msg.covariance[0] - offset   # yaw
            self.data.data[10] = msg.covariance[1] - offset   # yaw_rate

            self.data.data[11] = msg.covariance[2] - offset
            self.data.data[12] = msg.covariance[3] - offset
            self.data.data[13] = msg.covariance[4] - offset
            self.data.data[14] = msg.covariance[5] - offset

            now = self.get_clock().now().nanoseconds * 1e-9
            self.data.data[-1] = now

            x_global = round(self.data.data[0], 3)
            y_global = round(self.data.data[1], 3)
            yaw_global = round(np.degrees(self.data.data[9]))

            self.get_logger().info(f'X_global: {x_global}, Y_global: {y_global}, Yaw_global: {yaw_global}')

            # Transformation to new frame
            theta = np.pi/2 + 0.545
            x_p = 0.43
            y_p = 0.54

            sin_theta = np.sin(theta)
            cos_theta = np.cos(theta)

            x_new = x_global * cos_theta + y_global * sin_theta - (x_p * cos_theta + y_p * sin_theta)
            y_new = -x_global * sin_theta + y_global * cos_theta + (x_p * sin_theta - y_p * cos_theta)

            yaw_new = pi_2_pi(round(self.data.data[9] - 3.686, 3))

            self.data_path.data[0] = x_new
            self.data_path.data[1] = y_new
            self.data_path.data[2] = yaw_new
            self.data_path.data[3] = round(np.degrees(yaw_new))

            self.get_logger().info(f'X_new: {x_new}, Y_new: {y_new}, Yaw_new_deg: {np.degrees(yaw_new)}\n')

            self.pub_estimate.publish(self.data)
            self.pub_path.publish(self.data_path)


def main(args=None):
    rclpy.init(args=args)
    node = ViconBridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()