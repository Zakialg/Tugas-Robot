import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from std_msgs.msg import Float64


class InverseKinematics(Node):

    def __init__(self):
        super().__init__('inverse_kinematics')

        self.wheel_radius = 0.1
        self.wheel_separation = 0.45

        self.create_subscription(
            Twist,
            '/input_ik',
            self.velocity_callback,
            10
        )

        self.left_publisher = self.create_publisher(
            Float64,
            '/left_wheel/command',
            10
        )

        self.right_publisher = self.create_publisher(
            Float64,
            '/right_wheel/command',
            10
        )

        self.cmd_vel_publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.get_logger().info('Inverse kinematics aktif.')

    def velocity_callback(self, msg):
        linear_speed = msg.linear.y
        angular_speed = msg.angular.z

        r = self.wheel_radius
        s = self.wheel_separation

        left_speed = (linear_speed - (s * angular_speed / 2.0)) / r
        right_speed = (linear_speed + (s * angular_speed / 2.0)) / r

        left_command = Float64()
        right_command = Float64()

        left_command.data = float(left_speed)
        right_command.data = float(right_speed)

        self.left_publisher.publish(left_command)
        self.right_publisher.publish(right_command)

        calculated_linear = (r / 2.0) * (right_speed + left_speed)
        calculated_angular = (r / s) * (right_speed - left_speed)

        cmd = Twist()
        cmd.linear.x = float(calculated_linear)
        cmd.angular.z = float(calculated_angular)

        self.cmd_vel_publisher.publish(cmd)

        self.get_logger().info(
            f'Input: v={linear_speed:.3f}, '
            f'omega={angular_speed:.3f} | '
            f'Wheel: L={left_speed:.3f}, '
            f'R={right_speed:.3f} | '
            f'cmd_vel: v={calculated_linear:.3f}, '
            f'omega={calculated_angular:.3f}'
        )


def main(args=None):
    rclpy.init(args=args)

    node = InverseKinematics()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
