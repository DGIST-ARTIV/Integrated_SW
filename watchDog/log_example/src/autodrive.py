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
import random
rclpy.init()
node = rclpy.create_node("autodrive")

while(1):
    #node.get_logger().error("fatal flagged")
    print("Random", random.random())
    time.sleep(5)
    if  random.random() >= 0.5:
    	node.get_logger().error("Type2 - Lane Uncertainty High")
    else:
        node.get_logger().fatal("Type1 - Lane Camera Connection Failed")
    #time.sleep(0.0000001)
