'''
써보려고 했는데, 이전 코드에서 pid 주기가 joint state의 callback에 종속되어있어서, pid의 주기를 통일하기 위해 callback쓰기로 결정
from multiprocessing import Process, Queue
import threading
'''
#for PID
import time

#ros2 module
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_default
from std_msgs.msg import Int16
from std_msgs.msg import Float32MultiArray
from sensor_msgs.msg import JointState

movecar_sub = '/move_car'

NODENAME = "move_ioniq"
rootname = '/dbw_cmd'

topic_Accel = '/Accel'
topic_Angular = '/Angular'
topic_Brake = '/Brake'
topic_Steer = '/Steer'
topic_Gear = '/Gear'

# move_car = [mode,speed,accel,brake,steer,gear,angular]

class Move_Ioniq(Node):

    def __init__(self):
        # Initializing move_ioniq node
        super().__init__(NODENAME)

        # Ioniq_info callback data
        self.infomsg = []

        # move_car callback data
        self.move_carmsg = [] #debug용 추후 제거 가능
        # About PID
        self.cur_time = time.time()
        self.prev_time = 0
        self.del_time = 0
        self.cur_vel = 0.0
        self.kp = 14
        self.ki = 0.25
        self.kd = 1
        self.error_p = 0
        self.error_i = 0
        self.error_d = 0
        self.prev_error = 0
        self.antiwindup = 70
        self.prev_desired_vel = 0
        self.mode1_data = [None] * 4

        # Initializing dbw_cmd_node publisher
        self.accelPub = self.create_publisher(Int16, rootname + topic_Accel, qos_profile_default)
        self.brakePub = self.create_publisher(Int16, rootname + topic_Brake, qos_profile_default)
        self.steerPub = self.create_publisher(Int16, rootname + topic_Steer, qos_profile_default)
        self.gearPub = self.create_publisher(Int16, rootname + topic_Gear, qos_profile_default)
        self.angularPub = self.create_publisher(Int16, rootname + topic_Angular, qos_profile_default)

        # Initializing dbw_ioniq_node subscriber
        self.JointSub = self.create_subscription(JointState, '/Joint_state', self.joint_callback, qos_profile_default)
        self.JointSub
        self.InfoSub = self.create_subscription(Float32MultiArray, '/Ioniq_info', self.info_callback, qos_profile_default)
        self.InfoSub

        # Initializing move_car topic subscriber
        self.move_carSub = self.create_subscription(Float32MultiArray, movecar_sub, self.move_car_callback, qos_profile_default)
        self.move_carSub

    def joint_callback(self, msg):
        self.cur_vel = msg.velocity[0]
        self.get_logger().info(f"joint_state_callback : velocity : {self.cur_vel}km/h")
        if self.mode1_data[0] == 1.0:
            self.pub_accel(self.mode1_data[2])
            self.pub_brake(self.mode1_data[3])
            self.get_logger().info(f"mode{self.mode1_data[0]}. {self.mode1_data[1]}km/h a: {self.mode1_data[2]}, b: {self.mode1_data[3]}")
            

    def info_callback(self, msg):
        self.infomsg = msg.data

    def move_car_callback(self, msg):
        self.move_carmsg = msg.data #debug
        self.get_logger().info(f"{self.move_carmsg}") #dubug
        mode = msg.data[0]
        if mode ==0.0: #E-STOP
            self.get_logger().info(f"E-STOP Publishing Actuator with mode{mode}")
            self.emergency_stop(msg)
            
        elif mode == 1.0: #straight road cruise control
            self.cruise_control(msg)

        elif mode == 2.0: #curved road cruise control
            pass

        elif mode == 3.0: #rapid deceleration
            pass

        elif mode == 4.0: #rapid acceleration
            pass 


              
    # Basic cmd publisher
    def pub(self, topic, val):
        topic_list = ['accel','brake','steer','gear','angular']

        if topic == topic_list[0]:
            val = int(val)
            if not 0 <= val <= 3000:
                raise ValueError(f"your val for accel, {val} is out of range.")
            accel = Int16()
            accel.data = val
            self.accelPub.publish(accel)

        elif topic == topic_list[1]:
            val = int(val)
            if not 0 <= val <= 29000:
                raise ValueError(f"your val for brake, {val} is out of range.")
            brake = Int16()
            brake.data = val
            self.brakePub.publish(brake)

        elif topic == topic_list[2]:
            val = int(val)
            if not -440 <= val <= 440:
                raise ValueError(f"your val for steer, {val} is out of range.")
            steer = Int16()
            steer.data = val
            self.steerPub.publish(steer)

        elif topic == topic_list[3]:
            gear_dict = {0:"parking",5:"driving",6:"neutral",7:"reverse"}            
            if val not in gear_dict:
                raise ValueError(f"your val for gear, {val} is not valid.")
            gear = Int16()
            gear.data = val
            self.gearPub.publish(gear)

        elif topic == topic_list[4]:
            val = int(val)
            if not 0 <= val <= 255:
                raise ValueError(f"your val for angular, {val} is out of range.")
            angular = Int16()
            angular.data = val
            self.angularPub.publish(angular)

        else:
            raise ValueError("your topic input is not valid.")

    #Functional cmd publishers
    def pub_accel(self, val):
        self.pub('accel', val)

    def pub_brake(self, val):
        self.pub('brake', val)

    def pub_steer(self, val):
        self.pub('steer', val)

    def pub_gear(self, val):
        self.pub('gear', val)

    def pub_angular(self, val):
        self.pub('angular', val)

    #mode manager

    #mode 0. Emergency Stop
    def emergency_stop(self, msg):
        self.pub_brake(msg.data[3])

    #mode 1. Cruise Control
    def PID(self,desired_vel):
        
        # When desired velocity is changed, prev_error and error_i should be reset! 
        if desired_vel != self.prev_desired_vel:
            self.prev_error = 0
            self.error_i = 0
        self.prev_desired_vel = desired_vel
        
        # Defining dt(del_time) 
        if self.prev_time ==0:
            self.prev_time = self.cur_time         
        self.cur_time = time.time()
        self.del_time = self.cur_time - self.prev_time

        # Calculate Errors
        self.error_p = desired_vel - self.cur_vel
        self.error_i += self.error_p * (self.del_time)
        time.sleep(0.005)
        if (self.error_i < - self.antiwindup):
            self.error_i = - self.antiwindup
        elif (self.error_i > self.antiwindup):
            self.error_i = self.antiwindup
        self.error_d = (self.error_p - self.prev_error)/self.del_time

        # PID Out
        pid_out = self.kp*self.error_p + self.ki*self.error_i + self.kd*self.error_d
        
        if pid_out > 1e5:
            pid_out = 1e5
        elif pid_out < -1e5:
            pid_out = -1e5

        # Feedback
        self.prev_error = self.error_p # Feedback current error
        self.prev_time = self.cur_time # Feedback current time

    	# accel_max - accel_dead_zone = 3000 - 800 = 2200
    	# 2200/10 = 220, 220 + 1 = 221
        if pid_out > 0:
            for i in range(221):
                if i <= pid_out < i+1:
                    return 800 + 10*i, 0

    	# brake_max - brake_dead_zone = 27000 - 3500 = 23500 (!!!!!!!should be changed to 29000 if needed!!!!!!!)
    	# 23500/10 = 2350, 2350 + 1 = 2351
        elif pid_out < 0:
            for i in range(2351):
                if i <= abs(pid_out) < i+1:
                    return 0, 3500+10*i

        return 0, 0

    def cruise_control(self,msg):
        self.mode1_data = [msg.data[0], msg.data[1]] + list(self.PID(msg.data[1]))
                 
def main(args=None):
    rclpy.init(args=args)
    move_car = Move_Ioniq()
    rclpy.spin(move_car)
    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    move_car.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
