# 2020.07.29.

# structure of move_car for Ioniq: [car_type = 0.0(Ioniq), mode, speed, accel, brake, steer, gear, angular(Ioniq), status(ERP42), estop(ERP42)]

#for PID
import time

#ros2 module
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_default
from std_msgs.msg import Int16
from std_msgs.msg import Float32MultiArray
from sensor_msgs.msg import JointState
from std_msgs.msg import String

NODENAME = "move_Ioniq"

#subscribed topics
topic_Movecar = '/move_car'
topic_Info = '/Ioniq_info'
topic_JointState = '/Joint_state'

#topics to be published
topic_MovecarInfo = '/move_car_info'

rootname = '/dbw_cmd'
topic_Accel = '/Accel'
topic_Angular = '/Angular'
topic_Brake = '/Brake'
topic_Steer = '/Steer'
topic_Gear = '/Gear'

class Move_Ioniq(Node):

    def __init__(self):
        # Initializing move_Ioniq node
        super().__init__(NODENAME)

        #callback data
        self.infomsg = [] # Ioniq_info
        self.cur_vel = 0.0 # JointState
        self.move_carmsg = [] #move_car(debug)
        self.move_car_info = "" #move_car_info
        self.prev_mode = 200.0

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
        self.mode_data = [None] * 4

        # Initializing Ioniq dbw_cmd_node publisher
        self.accelPub = self.create_publisher(Int16, rootname + topic_Accel, qos_profile_default)
        self.brakePub = self.create_publisher(Int16, rootname + topic_Brake, qos_profile_default)
        self.steerPub = self.create_publisher(Int16, rootname + topic_Steer, qos_profile_default)
        self.gearPub = self.create_publisher(Int16, rootname + topic_Gear, qos_profile_default)
        self.angularPub = self.create_publisher(Int16, rootname + topic_Angular, qos_profile_default)

        # Initializing dbw_ioniq_node subscriber
        self.JointSub = self.create_subscription(JointState, topic_JointState, self.joint_callback, qos_profile_default)
        self.JointSub
        self.InfoSub = self.create_subscription(Float32MultiArray, topic_Info, self.info_callback, qos_profile_default)
        self.InfoSub

        # Initializing move_car topic subscriber
        self.move_carSub = self.create_subscription(Float32MultiArray, topic_Movecar, self.move_car_callback, qos_profile_default)
        self.move_carSub

        # Initializing move_car_info topic publisher (depends on move_car callback)
        self.MovecarInfoPub = self.create_publisher(String, topic_MovecarInfo, qos_profile_default)
        self.timer = self.create_timer(0.5, self.timer_callback)

    def timer_callback(self):
        if len(self.move_carmsg)!=0:
            car_type = ""
            if self.move_carmsg[0] == 0.0:
                car_type = "Ioniq"
            elif self.move_carmsg[0] == 1.0:
                car_type = "ERP42"

            mode = ""
            if self.move_carmsg[1] == 0.0:
                mode = "E-Stop"
            elif self.move_carmsg[1] == 1.0:
                mode = "Cruise Control"
            elif self.move_carmsg[1] == 2.0:
                mode = "Cruise Control with Steering"
            elif self.move_carmsg[1] == 3.0:
                mode = "Developer Mode"
            elif self.move_carmsg[1] == 4.0:
                mode = "Cruise Control with Developer Mode"

            else:
                self.get_logger().warn("Wrong Mode for move_Ioniq!!!")
            move_car_info = String()
            move_car_info.data = f'Car Type : {self.move_carmsg[0]}. {car_type}\nMode : {self.move_carmsg[1]}. {mode}\nCurrent Speed: {self.cur_vel}'
            self.MovecarInfoPub.publish(move_car_info)
            self.get_logger().info('Publishing: "%s"' % move_car_info)
            

    def joint_callback(self, msg):
        self.cur_vel = msg.velocity[0]

        if self.mode_data[0] == 1.0 or self.mode_data[0] == 2.0 or self.mode_data[0] ==4.0: # for PID
            self.mode_data[2], self.mode_data[3] = self.PID(self.mode_data[1])
            self.pub_accel(self.mode_data[2])
            self.pub_brake(self.mode_data[3])
            self.mode_data[1] = self.prev_desired_vel
            self.get_logger().info(f"mode{self.mode_data[0]}. {self.mode_data[1]}km/h a: {self.mode_data[2]}, b: {self.mode_data[3]}")
           
    def info_callback(self, msg):
        self.infomsg = msg.data

    # structure of move_car for Ioniq: [car_type = 0.0(Ioniq), mode, speed, accel, brake, steer, gear, angular(Ioniq), status(ERP42), estop(ERP42)]
    def move_car_callback(self, msg):
        self.get_logger().info(f"{msg.data}")
        if self.prev_mode == 200.0 and len(msg.data) ==1 and msg.data[0] == 119.0: #case 0. when the reset code is the first published code
            self.prev_mode == 119.0
            self.get_logger().warn("You published E-Stop reset code as the first topic!")
 
        elif self.prev_mode == 119.0 and len(msg.data) ==1 and msg.data[0] == 119.0: #case 1. reset many times repeatly
            self.prev_mode = 119.0
            self.get_logger().warn("Don't reset too much!")

        elif self.prev_mode !=0.0 and len(msg.data) == 1 and msg.data[0] == 119.0: #case 2. reset after other modes except E-Stop mode 
            self.prev_mode = 119.0
            self.get_logger().warn("Reset after other modes except E-Stop mode.")

        elif self.prev_mode !=0.0:

            if len(msg.data) != 10 or msg.data[0] != 0.0: #wrong topics
                self.get_logger().warn(f"You published wrong!!! {msg.data}")
            else:
                self.prev_mode = msg.data[1]
                self.move_carmsg = msg.data #debug
                self.get_logger().info(f"{self.move_carmsg}") #dubug
                mode = msg.data[1]

                if mode ==0.0: #E-STOP
                    self.mode_data[0] = 0.0
                    self.get_logger().warn(f"E-STOP Publishing Actuator with mode{mode}")
                    self.emergency_stop(msg)

                elif mode == 1.0: #cruise control
                    self.cruise_control(msg)

                elif mode == 2.0: #cruise control with steering
                    steer = msg.data[5]
                    angular = msg.data[7]
                    self.pub_angular(angular)
                    self.pub_steer(steer)
                    self.cruise_control(msg)

                elif mode == 3.0: # mode that you can directly publish cmd value (for develper mode.)
                    self.mode_data[0] = 3.0                
                    accel = msg.data[3]
                    brake = msg.data[4]
                    steer = msg.data[5]
                    gear = msg.data[6]
                    angular = msg.data[7]
                    self.pub_accel(accel)
                    self.pub_brake(brake)
                    self.pub_angular(angular)
                    self.pub_steer(steer)
                    self.pub_gear(gear)

                elif mode == 4.0: # mode 1.0 + mode 3.0 (cruise control and direct publish except accel and brake)
                    steer = msg.data[5]
                    gear = msg.data[6]
                    angular = msg.data[7]
                    self.cruise_control(msg)
                    self.pub_angular(angular)
                    self.pub_steer(steer)
                    self.pub_gear(gear)            

                elif mode == 5.0: # cruise control without
                    pass
                

        elif self.prev_mode == 0.0:

            if len(msg.data) == 1 and msg.data[0] ==119.0: #escape code [119.0]
                self.prev_mode = 119.0
                self.get_logger().info("Escape!")
            else:
                self.get_logger().info(f"Stucked in E-Stop! {msg.data}")

        else:
            self.get_logger().warn(f"Not Valid Message!!! {msg.data}")


            

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
            val = int(val)
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
        self.pub_brake(msg.data[4])

    #mode 1. Cruise Control
    def PID(self,desired_vel):

        if desired_vel == -1.0:
            desired_vel = self.prev_desired_vel
        
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
        self.pid_out = pid_out
        if pid_out > 1000:
            pid_out = 1000
        elif pid_out < -1000:
            pid_out = -1000

        self.prev_error = self.error_p # Feedback current error
        self.prev_time = self.cur_time # Feedback current time

    	# accel_max - accel_dead_zone = 3000 - 800 = 2200
    	# 2200/10 = 220, 220 + 1 = 221 
        '''
        if pid_out > 0:
            for i in range(221):
                if i <= pid_out < i+1:
                    return 800 + 10*i, 0
        '''
        if pid_out > 0:
            for i in range(858):
                if i <= pid_out < i+1:
                    gaspedal = 800 + 10*i
                    if gaspedal >= 3000:
                        gaspedal = 3000
                        return gaspedal, 0
                    else:
                        return gaspedal, 0
        

    	# brake_max - brake_dead_zone = 29000 - 3500 = 25500 (!!!!!!!should be changed to 29000 if needed!!!!!!!)
    	# 25500/10 = 2550, 2550 + 1 = 2551
        elif pid_out < 0:
            for i in range(2551):
                if i <= abs(pid_out) < i+1:
                    return 0, 2700+10*i

        return 0, 0

    def cruise_control(self,msg):
        self.mode_data = [msg.data[1], msg.data[2], 0.0, 0.0]
                 
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
