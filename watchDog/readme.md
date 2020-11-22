### 종속성
  1. sudo apt install python3-pyqt5.qtmultimedia
  2. sudo apt-get install libqt5multimedia5-plugins



### 에러 레벨

  1. ROS_INFO, ROS_DEBUG - 출력, 경고 없음.
  2. ROS_WARNING - 출력, Level2 부드러운 알림
  3. ROS_ERROR, FATAL - Level3 - 반복적인 Beep 음
  
### 로그 Pub
```cpp
//roscpp
ROS_INFO("recieve msg: %d", msg->data);
ROS_WARNING(...);
ROS_FATAL(...);
```

```py
#rospy
rospy.logdebug(msg, *args)
rospy.logwarn(msg, *args)
rospy.loginfo(msg, *args)
rospy.logerr(msg, *args)
rospy.logfatal(msg, *args)
```

```py
# rclpy
rclpy.init(args=args)
node = rclpy.create_node('minimal_client')
node.get_logger().info('service not available, waiting again...')

```



### 프로그램
  1. 경고 발생시 Disarm 버튼을 눌러 해제합니다. 해제하면 10초간은 동일한 경고등급은 재알림되지 않습니다.
  2. 프로그램 상에서 알림여부를 끌 수 있습니다.
