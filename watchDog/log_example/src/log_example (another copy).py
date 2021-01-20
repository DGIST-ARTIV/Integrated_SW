## Log Test

'''
DEBUG = 10
ERROR = 40
FATAL = 50
INFO = 20
UNSET = 0
WARN = 30


You can get this enum from rqt /rosout topic
'''



import rclpy
import time

rclpy.init()
node = rclpy.create_node("rclpy_log_test")

while(1):
    node.get_logger().error("fatal flagged")


    node.get_logger().warning("fatal flagged")
    time.sleep(0.0000001)
