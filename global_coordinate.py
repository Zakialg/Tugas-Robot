
import math

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist


class GlobalCoordinate(Node):

    def __init__(self):
        super().__init__('global_coordinate_node')

        self.wheel_radius = 0.1
        self.wheel_separation = 0.45

        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0

        self.last_time = self.get_clock().now()

        self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10
        )

        self.get_logger().info(
            'Global coordinate node aktif. Menunggu data /cmd_vel...'
        )

    def cmd_vel_callback(self, msg):
        current_time = self.get_clock().now()
        dt = (current_time - self.last_time).nanoseconds / 1e9
        self.last_time = current_time

        if dt <= 0.0:
            return

        v_b = msg.linear.x
        omega = msg.angular.z

        r = self.wheel_radius
        s = self.wheel_separation

        v_l = v_b - (s * omega / 2.0)
        v_r = v_b + (s * omega / 2.0)

        phi_dot_l = v_l / r
        phi_dot_r = v_r / r

        theta = self.theta

        x_dot = (r / 2.0) * math.cos(theta) * phi_dot_l + \
                (r / 2.0) * math.cos(theta) * phi_dot_r

        y_dot = (r / 2.0) * math.sin(theta) * phi_dot_l + \
                (r / 2.0) * math.sin(theta) * phi_dot_r

        theta_dot = (-r / s) * phi_dot_l + (r / s) * phi_dot_r

        self.x += x_dot * dt
        self.y += y_dot * dt
        self.theta += theta_dot * dt

        self.get_logger().info(
            f'x_dot={x_dot:.3f}, y_dot={y_dot:.3f}, theta_dot={theta_dot:.3f}'
        )


def main(args=None):
    rclpy.init(args=args)

    node = GlobalCoordinate()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
