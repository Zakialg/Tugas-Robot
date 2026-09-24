import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time
import math

class SquareMoverNode(Node):
    def __init__(self):
        super().__init__('square_mover_node')

        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.start_time = time.time()

        self.panjang = 3.0
        self.lebar = 1.5

        self.kecepatan_linear = 0.5
        self.kecepatan_angular = 0.5

        self.waktu_panjang = self.panjang / self.kecepatan_linear
        self.waktu_lebar = self.lebar / self.kecepatan_linear

        self.waktu_belok = (math.pi / 2) / self.kecepatan_angular

        self.sequence = [
            (self.waktu_panjang, self.kecepatan_linear, 0.0, 'Maju sisi 1 (panjang)...'),
            (self.waktu_belok, 0.0, -self.kecepatan_angular, 'Belok kanan 90 derajat...'),
            (self.waktu_lebar, self.kecepatan_linear, 0.0, 'Maju sisi 2 (lebar)...'),
            (self.waktu_belok, 0.0, -self.kecepatan_angular, 'Belok kanan 90 derajat...'),
            (self.waktu_panjang, self.kecepatan_linear, 0.0, 'Maju sisi 3 (panjang)...'),
            (self.waktu_belok, 0.0, -self.kecepatan_angular, 'Belok kanan 90 derajat...'),
            (self.waktu_lebar, self.kecepatan_linear, 0.0, 'Maju sisi 4 (lebar)...'),
            (self.waktu_belok, 0.0, -self.kecepatan_angular, 'Belok kanan 90 derajat (kembali ke titik awal)...'),
        ]

        self.batas_waktu = []
        total = 0.0
        for durasi, _, _, _ in self.sequence:
            total += durasi
            self.batas_waktu.append(total)

        self.get_logger().info(
            f'Lintasan: {self.panjang}m x {self.lebar}m | '
            f'Total waktu tempuh: {total:.2f} detik'
        )

    def timer_callback(self):
        msg = Twist()
        elapsed_time = time.time() - self.start_time

        fase_aktif = None
        for i, batas in enumerate(self.batas_waktu):
            if elapsed_time < batas:
                fase_aktif = i
                break

        if fase_aktif is not None:
            _, linear, angular, label = self.sequence[fase_aktif]
            msg.linear.x = linear
            msg.angular.z = angular
            self.get_logger().info(label)
            self.publisher_.publish(msg)
        else:
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            self.get_logger().info('Selesai. Robot kembali ke titik awal.')
            self.publisher_.publish(msg)

            self.timer.cancel()
            rclpy.shutdown()
            return


def main(args=None):
    rclpy.init(args=args)
    node = SquareMoverNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()


if __name__ == '__main__':
    main()
