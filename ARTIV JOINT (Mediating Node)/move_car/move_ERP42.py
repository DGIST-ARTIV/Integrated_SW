# structure of move_car for ERP42: [car_type = 1.0(ERP42), mode, speed, accel, brake, steer, gear, status, estop]

#for PID
import time

#ros2 module
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_default
from std_msgs.msg import Int16
from std_msgs.msg import Float32MultiArray
from sensor_msgs.msg import JointState

NODENAME = "move_ERP42"

#subscribed topics
topic_Movecar = '/move_car'
topic_Info = '/ERP42_info'
topic_JointState = '/JointState'

#topics to be published
rootname = '/dbw_cmd'
topic_Accel = '/Accel'
topic_Brake = '/Brake'
topic_Steer = '/Steer'
topic_Gear = '/Gear'
topic_Status = '/Status'
topic_Estop = '/Estop'

class Move_ERP42(Node):

    def __init__(self):
        # Initializing move_ERP42 node
        super().__init__(NODENAME)

        #callback data
        self.infomsg = []     # ERP42_info
        self.cur_vel = 0.0    # JointState
        self.move_carmsg = [] # move_car(debug)

        # About PID
        self.cur_time = time.time()
        self.prev_time = 0
        self.del_time = 0
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

        # Initializing ERP42 dbw_cmd_node publisher
        self.accelPub = self.create_publisher(Int16, rootname + topic_Accel, qos_profile_default)
        self.brakePub = self.create_publisher(Int16, rootname + topic_Brake, qos_profile_default)
        self.steerPub = self.create_publisher(Int16, rootname + topic_Steer, qos_profile_default)
        self.gearPub = self.create_publisher(Int16, rootname + topic_Gear, qos_profile_default)
        self.statusPub = self.create_publisher(Int16, rootname + topic_Status, qos_profile_default)
        self.estopPub = self.create_publisher(Int16, rootname + topic_Estop, qos_profile_default)

        # Initializing dbw_erp42_node subscriber
        self.JointSub = self.create_subscription(JointState, topic_JointState, self.joint_callback, qos_profile_default)
        self.JointSub
        self.InfoSub = self.create_subscription(Float32MultiArray, topic_Info, self.info_callback, qos_profile_default)
        self.InfoSub

        # Initializing move_car topic subscriber
        self.move_carSub = self.create_subscription(Float32MultiArray, topic_Movecar, self.move_car_callback, qos_profile_default)
        self.move_carSub

    def joint_callback(self, msg):
        self.cur_vel = msg.velocity[0]

        if self.mode1_data[0] == 1.0: #for PID
            self.pub_accel(self.mode1_data[2])
            self.pub_brake(self.mode1_data[3])
            self.get_logger().info(f"mode{self.mode1_data[0]}. {self.mode1_data[1]}km/h a: {self.mode1_data[2]}, b: {self.mode1_data[3]}")

    def info_callback(self, msg):
        self.infomsg = msg.data

    # structure of move_car for ERP42: [car_type = 1.0(ERP42), mode, speed, accel, brake, steer, gear, status, estop]
    def move_car_callback(self, msg):
        self.move_carmsg = msg.data #debug
        self.get_logger().info(f"move_car : {self.move_carmsg}") #dubug
        mode = msg.data[1]

        if mode ==0.0: #E-STOP
            self.get_logger().info(f"E-STOP Publishing Actuator with mode{mode}")
            self.emergency_stop()
# ERP42의 accel topic값은 raw accel값이 아닌 실제 속도를 발행한다. (ex) 200일 경우 20km/h
        elif mode == 1.0: #이 부분은 승기 pid를 위해 있음
            self.cruise_control(msg)

        elif mode == 2.0: # publish raw velocity
            self.raw_cruise_control(msg)

        elif mode == 3.0: #cmd값 직접 발행할 수 있는 모드(개발자용)
            accel = msg.data[3]
            brake = msg.data[4]
            steer = msg.data[5]
            gear = msg.data[6]
            status = msg.data[7]
            estop = msg.data[8]
            self.pub_accel(accel)
            self.pub_brake(brake)
            self.pub_steer(steer)
            self.pub_gear(gear)
            self.pub_status(status)
            self.pub_estop(estop)

        elif mode == 4.0: #rapid acceleration
            pass 


              
    # Basic ERP42 cmd publisher
    def pub(self, topic, val):
        topic_list = ['accel','brake','steer','gear','status', 'estop']

        if topic == topic_list[0]:
            val = int(val)
            if not 0 <= val <= 200:
                raise ValueError(f"your val for accel, {val} is out of range.")
            accel = Int16()
            accel.data = val
            self.accelPub.publish(accel)

        elif topic == topic_list[1]:
            val = int(val)
            if not 0 <= val <= 200:
                raise ValueError(f"your val for brake, {val} is out of range.")
            brake = Int16()
            brake.data = val
            self.brakePub.publish(brake)

        elif topic == topic_list[2]:
            val = int(val)
            if not -2000 <= val <= 2000:
                raise ValueError(f"your val for steer, {val} is out of range.")
            steer = Int16()
            steer.data = val
            self.steerPub.publish(steer)

        elif topic == topic_list[3]:
            val = int(val)
            gear_dict = {0:"Forward",5:"Neutral",2:"Backward"}            
            if val not in gear_dict:
                raise ValueError(f"your val for gear, {val} is not valid.")
            gear = Int16()
            gear.data = val
            self.gearPub.publish(gear)

        elif topic == topic_list[4]:
            val = int(val)
            status_dict = {0:"Manual",1:"Auto"} #default is manual            
            if val not in status_dict:
                raise ValueError(f"your val for status, {val} is not valid.")
            status = Int16()
            status.data = val
            self.statusPub.publish(status)

        elif topic == topic_list[5]:
            val = int(val)
            estop_dict = {0:"E-Stop Off",1:"E-Stop ON"} #default is E-Stop Off            
            if val not in estop_dict:
                raise ValueError(f"your val for estop, {val} is not valid.")
            estop = Int16()
            estop.data = val
            self.estopPub.publish(estop)

        else:
            raise ValueError("your topic input is not valid.")

    #Functional ERP42 cmd publishers
    def pub_accel(self, val):
        self.pub('accel', val)

    def pub_brake(self, val):
        self.pub('brake', val)

    def pub_steer(self, val):
        self.pub('steer', val)

    def pub_gear(self, val):
        self.pub('gear', val)

    def pub_status(self, val):
        self.pub('status', val)

    def pub_estop(self, val):
        self.pub('estop', val)

    #mode manager

    #mode 0.0. Emergency Stop
    def emergency_stop(self):
        self.pub_estop(1.0)

    #mode 1.0. Cruise Control
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
        self.mode1_data = [msg.data[1], msg.data[2]] + list(self.PID(msg.data[1]))
    
    def raw_cruise_control(self,msg):
        self.pub_accel(msg.data[2]*10)
                 
def main(args=None):
    rclpy.init(args=args)
    move_ERP42 = Move_ERP42()
    rclpy.spin(move_ERP42)
    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    move_ERP42.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
