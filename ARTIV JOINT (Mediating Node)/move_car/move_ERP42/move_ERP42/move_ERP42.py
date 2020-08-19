# 2020.08.20.

# structure of move_car for ERP42: [car_type = 1.0(ERP42), mode, speed, accel, brake, steer, gear, angular(Ioniq), status(ERP42), estop(ERP42)]

#for PID
import time

#ros2 module
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_default
from std_msgs.msg import Int16
from std_msgs.msg import Float32MultiArray
from std_msgs.msg import Float64
from std_msgs.msg import String

pid_speed_limit = 7.0

NODENAME = "move_ERP42"

#subscribed topics
topic_Movecar = '/move_car'
topic_Info = '/ERP42_info'
topic_GpsSpd = '/gps_spd'
topic_NavPilot = '/mission_manager/nav_pilot' 

#topics to be published
topic_MovecarInfo = '/move_car_info'

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
        self.cur_vel = 0.0    # GPS_SPEED
        self.move_carmsg = [] # move_car(debug)
        self.move_car_info = "" #move_car_info
        self.prev_mode = 200.0
        self.nav_pilot_switch = 2
        self.temp_nav_pilotmsg = []

        # About PID
        self.tartget_speed = 0.0
        self.cur_time = time.time()
        self.prev_time = 0
        self.del_time = 0
        self.kp = 15
        self.ki = 3
        self.kd = 2
        self.error_p = 0
        self.error_i = 0
        self.error_d = 0
        self.prev_error = 0
        self.antiwindup = 40.0
        self.prev_desired_vel = 0
        self.mode_data = [None] * 4

        # Initializing ERP42 dbw_cmd_node publisher
        self.accelPub = self.create_publisher(Int16, rootname + topic_Accel, qos_profile_default)
        self.brakePub = self.create_publisher(Int16, rootname + topic_Brake, qos_profile_default)
        self.steerPub = self.create_publisher(Int16, rootname + topic_Steer, qos_profile_default)
        self.gearPub = self.create_publisher(Int16, rootname + topic_Gear, qos_profile_default)
        self.statusPub = self.create_publisher(Int16, rootname + topic_Status, qos_profile_default)
        self.estopPub = self.create_publisher(Int16, rootname + topic_Estop, qos_profile_default)

        # Initializing dbw_erp42_node subscriber
        self.GpsSpdSub = self.create_subscription(Float64, topic_GpsSpd, self.gps_spd_callback, qos_profile_default)
        self.GpsSpdSub
        self.InfoSub = self.create_subscription(Float32MultiArray, topic_Info, self.info_callback, qos_profile_default)
        self.InfoSub

        # Initializing Navigation Pilot switch subscriber
        self.NavPilotSub = self.create_subscription(Int16, topic_NavPilot, self.nav_pilot_callback, qos_profile_default)
        self.NavPilotSub

        # Initializing move_car topic subscriber
        self.move_carSub = self.create_subscription(Float32MultiArray, topic_Movecar, self.move_car_callback, qos_profile_default)
        self.move_carSub

        # Initializing move_car_info topic publisher (depends on move_car callback)
        self.MovecarInfoPub = self.create_publisher(String, topic_MovecarInfo, qos_profile_default)
        self.timer = self.create_timer(0.5, self.timer_callback)

    def nav_pilot_callback(self, msg):
        self.nav_pilot_switch = msg.data        

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
            elif self.move_carmsg[1] == 5.0:
                mode = "Navigation Pilot Mode"
            elif self.move_carmsg[1] == 6.0:
                mode = "Mission Manager Mode"
            else:
                self.get_logger().warn("Wrong Mode for move_ERP42!!!")

            move_car_info = String()
            move_car_info.data = f'Car Type : {self.move_carmsg[0]}. {car_type}\nMode : {self.move_carmsg[1]}. {mode}\nCurrent Speed: {self.cur_vel}'
            self.MovecarInfoPub.publish(move_car_info)
            self.get_logger().info('Publishing: "%s"' % move_car_info)

    def gps_spd_callback(self, msg):
        self.cur_vel = msg.data

        if self.mode_data[0] == 1.0 or self.mode_data[0] == 2.0 or self.mode_data[0] ==4.0: # for PID
            self.mode_data[2], self.mode_data[3] = self.PID(self.mode_data[1])
            self.pub_accel(self.mode_data[2])
            self.pub_brake(self.mode_data[3])   
            self.mode_data[1] = self.prev_desired_vel
            self.get_logger().info(f"cruise_mode{self.mode_data[0]}. {self.mode_data[1]}km/h a: {self.mode_data[2]}, b: {self.mode_data[3]}")

        elif self.tartget_speed <= pid_speed_limit and self.mode_data[0] == 5.0:
            self.mode_data[2], self.mode_data[3] = self.PID(self.mode_data[1])
            self.pub_accel(self.mode_data[2])
            self.pub_brake(self.mode_data[3])   
            self.mode_data[1] = self.prev_desired_vel
            self.get_logger().info(f"cruise_mode{self.mode_data[0]}. {self.mode_data[1]}km/h a: {self.mode_data[2]}, b: {self.mode_data[3]}")

        elif self.tartget_speed <= pid_speed_limit and self.mode_data[0] == 6.0:
            self.mode_data[2], self.mode_data[3] = self.PID(self.mode_data[1])
            self.pub_accel(self.mode_data[2])
            self.pub_brake(self.mode_data[3])   
            self.mode_data[1] = self.prev_desired_vel
            self.get_logger().info(f"cruise_mode{self.mode_data[0]}. {self.mode_data[1]}km/h a: {self.mode_data[2]}, b: {self.mode_data[3]}")

    def info_callback(self, msg):
        self.infomsg = msg.data

    # structure of move_car for ERP42: [car_type = 1.0(ERP42), mode, speed, accel, brake, steer, gear, angular(Ioniq), status(ERP42), estop(ERP42)]
    def move_car_callback(self, msg):
        self.get_logger().info(f"{msg.data}")
        if self.prev_mode == 200.0 and len(msg.data) ==1 and msg.data[0] == 119.0: #case 0. when the reset code is the first published code
            self.prev_mode = 119.0
            self.get_logger().warn("You published E-Stop reset code as the first topic!")
 
        elif self.prev_mode == 119.0 and len(msg.data) ==1 and msg.data[0] == 119.0: #case 1. reset many times repeatly
            self.prev_mode = 119.0
            self.get_logger().warn("Don't reset too much!")

        elif self.prev_mode !=0.0 and len(msg.data) == 1 and msg.data[0] == 119.0: #case 2. reset after other modes except E-Stop mode 
            self.prev_mode = 119.0
            self.get_logger().warn("Reset after other modes except E-Stop mode.")

        elif self.prev_mode !=0.0:

            if len(msg.data) != 10 or msg.data[0] != 1.0: #wrong topics
                self.get_logger().warn(f"You published wrong!!! {msg.data}")
            else:
                mode = msg.data[1]

                if self.nav_pilot_switch == 0 and mode == 6.0: # mission manager mode
                    if self.prev_mode == 119.0:
                        self.emergency_stop_off()
                    steer = msg.data[5]
                    gear = msg.data[6]
                    speed = msg.data[2]
                    if speed > pid_speed_limit:
                        self.mode_data[0] = 6.0
                        self.pub_accel(speed*10)
                        self.prev_error = 0
                        self.error_i = 0
                        self.prev_desired_vel = 0
                    elif speed <= pid_speed_limit:
                        self.cruise_control(msg)

                    self.pub_steer(steer)
                    self.pub_gear(gear)
                    self.prev_mode = msg.data[1]
                    self.move_carmsg = msg.data #debug
                    self.get_logger().info(f"{self.move_carmsg}") #dubug

                elif mode ==0.0: #E-STOP
                    self.get_logger().warn(f"E-STOP Publishing Actuator with mode{mode}")
                    self.emergency_stop_on()
                    self.mode_data[0] = 0.0
                    self.prev_mode = msg.data[1]
                    self.move_carmsg = msg.data #debug
                    self.get_logger().info(f"{self.move_carmsg}") #dubug
                    self.prev_error = 0
                    self.error_i = 0
                    self.prev_desired_vel = 0

                elif mode == 1.0: #cruise control
                    if self.prev_mode == 119.0:
                        self.emergency_stop_off()
                    self.cruise_control(msg)
                    self.prev_mode = msg.data[1]
                    self.move_carmsg = msg.data #debug
                    self.get_logger().info(f"{self.move_carmsg}") #dubug

                elif mode == 2.0: #cruise control with steering
                    if self.prev_mode == 119.0:
                        self.emergency_stop_off()
                    steer = msg.data[5]
                    self.pub_steer(steer)
                    self.cruise_control(msg)
                    self.prev_mode = msg.data[1]
                    self.move_carmsg = msg.data #debug
                    self.get_logger().info(f"{self.move_carmsg}") #dubug

                elif mode == 3.0: # mode that you can directly publish cmd value (for develper mode.)
                    if self.prev_mode == 119.0:
                        self.emergency_stop_off()
                    self.mode_data[0] = 3.0               
                    accel = msg.data[3]
                    brake = msg.data[4]
                    steer = msg.data[5]
                    gear = msg.data[6]
                    self.pub_accel(accel)
                    self.pub_brake(brake)
                    self.pub_steer(steer)
                    self.pub_gear(gear)
                    self.prev_mode = msg.data[1]
                    self.move_carmsg = msg.data #debug
                    self.get_logger().info(f"{self.move_carmsg}") #dubug
                    self.prev_error = 0
                    self.error_i = 0
                    self.prev_desired_vel = 0

                elif mode == 4.0: # mode 1.0 + mode 3.0 (cruise control and direct publish except accel and brake)
                    if self.prev_mode == 119.0:
                        self.emergency_stop_off()
                    steer = msg.data[5]
                    gear = msg.data[6]
                    self.cruise_control(msg)
                    self.pub_steer(steer)
                    self.pub_gear(gear)
                    self.prev_mode = msg.data[1]
                    self.move_carmsg = msg.data #debug
                    self.get_logger().info(f"{self.move_carmsg}") #dubug

                elif mode == 5.0: # navigation pilot mode
                    if self.nav_pilot_switch == 0: #switch off
                      pass  

                    elif self.nav_pilot_switch ==1:                    
                        if self.prev_mode == 119.0:
                            self.emergency_stop_off()
                        steer = msg.data[5]
                        gear = msg.data[6]
                        self.tartget_speed = msg.data[2]
                        if self.tartget_speed > pid_speed_limit:
                            self.mode_data[0] = 5.0
                            self.pub_accel(self.tartget_speed*10)
                            self.prev_error = 0
                            self.error_i = 0
                            self.prev_desired_vel = 0
                        elif self.tartget_speed <= pid_speed_limit:
                            self.cruise_control(msg)

                        self.pub_steer(steer)
                        self.pub_gear(gear)
                        self.temp_nav_pilotmsg = msg.data                   
                        self.prev_mode = msg.data[1]
                        self.move_carmsg = msg.data #debug
                        self.get_logger().info(f"{self.move_carmsg}") #dubug

                elif self.nav_pilot_switch == 1 and mode == 6.0: # mission manager mode - decrease velocity!
                    if self.prev_mode == 119.0:
                        self.emergency_stop_off()
                    steer = self.temp_nav_pilotmsg[5]
                    gear = self.temp_nav_pilotmsg[6]
                    self.tartget_speed = msg.data[2]
                    if self.tartget_speed > pid_speed_limit:
                        self.mode_data[0] = 6.0
                        self.pub_accel(self.tartget_speed*10)
                        self.prev_error = 0
                        self.error_i = 0
                        self.prev_desired_vel = 0
                    elif self.tartget_speed <= pid_speed_limit:
                        self.cruise_control(msg)

                    self.pub_steer(steer)
                    self.pub_gear(gear) 
                    self.prev_mode = msg.data[1]
                    self.move_carmsg = msg.data #debug
                    self.get_logger().info(f"{self.move_carmsg}") #dubug                

        elif self.prev_mode == 0.0:

            if len(msg.data) == 1 and msg.data[0] ==119.0: #escape code [119.0]
                self.prev_mode = 119.0
                self.get_logger().info("Escape!")
            else:
                self.get_logger().info(f"Stucked in E-Stop! {msg.data}")

        else:
            self.get_logger().warn(f"Not Valid Message!!! {msg.data}")
              
    # Basic ERP42 cmd publisher
    def pub(self, topic, val):
        topic_list = ['accel','brake','steer','gear','status', 'estop']

        if topic == topic_list[0]:
            val = int(val)
            if not 0 <= val <= 200:
                self.get_logger().info(f"your val for accel, {val} is out of range.")
            accel = Int16()
            accel.data = val
            self.accelPub.publish(accel)

        elif topic == topic_list[1]:
            val = int(val)
            if not 0 <= val <= 200:
                self.get_logger().info(f"your val for brake, {val} is out of range.")
            brake = Int16()
            brake.data = val
            self.brakePub.publish(brake)

        elif topic == topic_list[2]:
            val = int(val)
            if not -2000 <= val <= 2000:
                self.get_logger().info(f"your val for steer, {val} is out of range.")
            steer = Int16()
            steer.data = val
            self.steerPub.publish(steer)

        elif topic == topic_list[3]:
            val = int(val)
            gear_dict = {0:"Forward",1:"Neutral",2:"Backward"}            
            if val not in gear_dict:
                self.get_logger().info(f"your val for gear, {val} is not valid.")
            gear = Int16()
            gear.data = val
            self.gearPub.publish(gear)

        elif topic == topic_list[4]:
            val = int(val)
            status_dict = {0:"Manual",1:"Auto"} #default is manual            
            if val not in status_dict:
                self.get_logger().info(f"your val for status, {val} is not valid.")
            status = Int16()
            status.data = val
            self.statusPub.publish(status)

        elif topic == topic_list[5]:
            val = int(val)
            estop_dict = {0:"E-Stop Off",1:"E-Stop ON"} #default is E-Stop Off            
            if val not in estop_dict:
                self.get_logger().info(f"your val for estop, {val} is not valid.")
            estop = Int16()
            estop.data = val
            self.estopPub.publish(estop)

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
    def emergency_stop_on(self):
        self.pub_estop(1.0)

    def emergency_stop_off(self):
        self.pub_estop(0.0)
        self.get_logger().info("E-Stop Off!")

    #mode 1. Cruise Control
    def PID(self,desired_vel):

        if desired_vel == -1.0 and self.prev_desired_Vel != -2.0:
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
        if (self.error_i < - self.antiwindup):
            self.error_i = - self.antiwindup
        elif (self.error_i > self.antiwindup):
            self.error_i = self.antiwindup
        self.error_d = (self.error_p - self.prev_error)/self.del_time

        # PID Out
        pid_out = self.kp*self.error_p + self.ki*self.error_i + self.kd*self.error_d
        self.pid_out = pid_out

        
        if pid_out > 500:
            pid_out = 500
        elif pid_out < -500:
            pid_out = -500


        self.prev_error = self.error_p # Feedback current error
        self.prev_time = self.cur_time # Feedback current time
 
    	# accel_max - accel_dead_zone = 200 - 0 = 200
    	# 2200/10 = 220, 220 + 1 = 221
        if pid_out > 0:
            for i in range(2001):
               if i <= 0.5*pid_out < i+1:
                    gaspedal = 2*i
                    if gaspedal >= 200:
                        gaspedal = 200
                        return int(gaspedal), 0
                    else:
                        return int(gaspedal), 0

    	# brake_max - brake_dead_zone = 200 - 0 = 200
    	# 23500/10 = 2350, 2350 + 1 = 2351
        elif pid_out < 0:
            for i in range(2001):
                if i <= 0.5*abs(pid_out) < i+1:
                    return 0, 2*i

        return 0, 0

    def cruise_control(self,msg):
        self.mode_data = [msg.data[1], msg.data[2], 0.0, 0.0]
                 
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
