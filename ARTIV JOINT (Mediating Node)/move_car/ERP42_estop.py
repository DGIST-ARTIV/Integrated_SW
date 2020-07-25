import rclpy
from rclpy.node import Node

from std_msgs.msg import Int16
from std_msgs.msg import Float32MultiArray
from rclpy.qos import qos_profile_default

class MinimalPublisher(Node):

    def __init__(self):
        super().__init__('move_car')
        self.publisher_ = self.create_publisher(Float32MultiArray, '/move_car',qos_profile_default)
        self.intmsg = Float32MultiArray()
        self.intmsg.data = [1.0,0.0]
        timer_period = 0.1  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        self.publisher_.publish(self.intmsg)
        self.get_logger().info('Publishing: "%s"' % self.intmsg.data)
        self.i += 1


def main(args=None):
    rclpy.init(args=args)

    minimal_publisher = MinimalPublisher()

    rclpy.spin(minimal_publisher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
