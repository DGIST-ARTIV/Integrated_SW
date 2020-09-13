# -*- coding: utf-8 -*-
# ARTIV SensorFusion v1.2

import rospy
#from tracking_msg.msg import TrackingObject, TrackingObjectArray


import glob, os
from time import sleep
import time
from std_msgs.msg import Int16, Float32MultiArray, Int16MultiArray, MultiArrayDimension
from std_msgs.msg import Int16MultiArray, String
from sensor_msgs.msg import JointState, Image, NavSatFix

from PyQt5.QtWidgets import *
import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtCore import *
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt


import sys
import numpy as np

sfUI = uic.loadUiType("emulator.ui")[0]

NODENAME = "mission_emulator"



class MyWindow(QMainWindow, sfUI):
    send_comm_request = pyqtSignal(str)
    proc_kill = pyqtSignal()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def _int(self, value):
        val = Int16()
        val.data = int(value)
        return val

    def __init__(self):
        super(QMainWindow, self).__init__()
        self.setupUi(self)
        self.setFixedSize(800, 646)
        self.center()

        self.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableWidget.setRowCount(6)

        self.tableWidget_2.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableWidget_2.setRowCount(4)

        rospy.init_node(NODENAME, anonymous = True)


        formUpdate = QTimer(self)
        formUpdate.start(10)
        formUpdate.timeout.connect(self.displayUpdate)


        self.pN = pubNode()
        self.sN = subNode()
        self.sN.start()

        self.dist = 0.0
        self.horizontalScrollBar.valueChanged.connect(self.distSet)

        self.pushButton.clicked.connect(self.setZero)
        self.pushButton_3.clicked.connect(self.sendRed)
        self.pushButton_5.clicked.connect(self.sendGreenLeft)
        self.pushButton_8.clicked.connect(self.sendGreen)
        self.pushButton_6.clicked.connect(self.sendRedYellow)
        self.pushButton_7.clicked.connect(self.sendYellow)
        self.pushButton_4.clicked.connect(self.sendRedLeft)
        self.pushButton_9.clicked.connect(self.sendUnknown)

        #self.comboBox.currentIndexChanged.connect(self.sendMission)

        self.pushButton_2.clicked.connect(self.setMission)

    def setZero(self):
        self.dist = 0.0
        self.horizontalScrollBar.setValue(0.0)

    def distSet(self):
        self.label_3.setText(str(self.horizontalScrollBar.value()))
        self.dist = self.horizontalScrollBar.value()

    def setMission(self):
        idx = self.comboBox.currentIndex()
        myidx = idx
        if idx == 0:
            # send zero
            pass
        elif idx > 13:
            myidx = idx + 7


        # myidx is mission paper base odx
        # idx is just idx of ease -1
        self.sendMission(idx, myidx)

    def sendMission(self, idx, myidx):
        msg = JointState()
        msg.name = [str(i) for i in [1, 2, 3, 4, 5, 6, 14, 15, 16, 17, 18, 19]]
        msg.position = [0.0] * 12

        if self.dist == 0:
            msg.position[idx-1] = 1.0

        msg2 = Float32MultiArray()
        msg2.data = [0.0] * 3
        msg2.data[0] = float(myidx)
        msg2.data[2] = float(self.dist)

        msg3 = Int16()
        msg3.data = myidx
        self.pN.signPub.publish(msg3)
        #self.pN.missionInfoPub.publish(msg)
        self.pN.nodeInfoPub.publish(msg2)



    def sendRed(self):
        msg = Int16()
        msg.data = 12
        self.pN.trafficPub.publish(msg)
    def sendUnknown(self):
        msg = Int16()
        msg.data = -1
        self.pN.trafficPub.publish(msg)
    def sendGreen(self):
        msg = Int16()
        msg.data = 11
        self.pN.trafficPub.publish(msg)
    def sendRedYellow(self):
        msg = Int16()
        msg.data = 8
        self.pN.trafficPub.publish(msg)
    def sendGreenLeft(self):
        msg = Int16()
        msg.data = 9
        self.pN.trafficPub.publish(msg)
    def sendYellow(self):
        msg = Int16()
        msg.data = 10
        self.pN.trafficPub.publish(msg)
    def sendRedLeft(self):
        msg = Int16()
        msg.data = 13
        self.pN.trafficPub.publish(msg)

    def displayUpdate(self):

        self.topicName1 = ['/dbw_cmd/Accel', '/dbw_cmd/Brake', '/dbw_cmd/Estop', 'dbw_cmd/Gear', 'dbw_cmd/Status', 'dbw_cmd/Steer']
        self.topicName2 = ['nav_pilot', 'nav_speed', 'mission_status', 'move_carmsg' ]
        try:
            for i in xrange(0, 6):
                self.tableWidget.setItem(i,0 , QTableWidgetItem(str(self.topicName1[i])))

                self.tableWidget.setItem(i, 1, QTableWidgetItem(str(self.sN.infoList1[i])))

            for i in xrange(0, 4):
                self.tableWidget_2.setItem(i, 0 , QTableWidgetItem(str(self.topicName2[i])))

                self.tableWidget_2.setItem(i, 1, QTableWidgetItem(str(self.sN.infoList2[i])))
        except Exception as ex:
            print(ex)
        pass

    node = 0


class subNode(QThread):
    def __init__(self):
        QThread.__init__(self)
        #        self.topicName1 = ['/dbw_cmd/Accel', '/dbw_cmd/Brake', '/dbw_cmd/Estop', 'dbw_cmd/Gear', 'dbw_cmd/Status', 'dbw_cmd/Steer']
        #     self.topicName2 = ['nav_pilot', 'nav_speed', 'mission_status', 'move_carmsg' ]
        #
        rospy.Subscriber('/dbw_cmd/Accel', Int16, self.accelCb)
        rospy.Subscriber('/dbw_cmd/Brake', Int16, self.brakeCb)
        rospy.Subscriber('/dbw_cmd/Estop', Int16, self.estopCb)
        rospy.Subscriber('/dbw_cmd/Status', Int16, self.statusCb)
        rospy.Subscriber('/dbw_cmd/Gear', Int16, self.gearCb)
        rospy.Subscriber('/dbw_cmd/Steer', Int16, self.steerCb)

        rospy.Subscriber('/mission_manager/nav_pilot', Int16, self.pilotCb)
        rospy.Subscriber('/mission_manager/nav_speed', Int16, self.speedCb)
        rospy.Subscriber('/mission_manager/mission_status', Int16, self.navStatusCb)
        rospy.Subscriber('/move_car', Float32MultiArray, self.moveInfo)
        #rospy.Subscriber('/lidar/tracking_objects', TrackingObjectArray, self.trackCb)
        #rospy.Subscriber('/enetsad/image', Image, self.imageCb)
        #rospy.Subscriber('/enetsad/info', Float32MultiArray, self.enetInfoCb)
        #rospy.Subscriber('/enetsad/cetnerPt', Float32MultiArray, self.enetCenterPt)
        #rospy.Subscriber('/TRT_yolov3/Bbox', Int16MultiArray, self.Bbox_callback)
        #rospy.Subscriber('/TRT_yolov3/result_image', Image, self.imageCb)
        self.infoList1 = [0] * 6
        self.infoList2 = [0] * 4


    def run(self):
        rospy.spin()

    def accelCb(self, msg):
        self.infoList1[0] = msg.data
    def brakeCb(self, msg):
        self.infoList1[1] = msg.data
    def estopCb(self, msg):
        self.infoList1[2] = msg.data
    def statusCb(self, msg):
        self.infoList1[3] = msg.data
    def gearCb(self, msg):
        self.infoList1[4] = msg.data
    def steerCb(self, msg):
        self.infoList1[5] = msg.data

    def pilotCb(self, msg):
        self.infoList2[0] = msg.data
    def speedCb(self, msg):
        self.infoList2[1] = msg.data
    def navStatusCb(self, msg):
        self.infoList2[2] = msg.data
    def moveInfo(self, msg):
        self.infoList2[3] = msg.data

class pubNode():
    def __init__(self):
        self.signPub = rospy.Publisher('/trt_yolov3_trackingResult/current_sign', Int16, queue_size = 1)
        self.trafficPub = rospy.Publisher('/trt_yolov3_trackingResult/current_trafficLight', Int16, queue_size = 1)
        #self.missionInfoPub = rospy.Publisher('/hdmap/mission_info', JointState, queue_size = 1)
        #self.nodeInfoPub = rospy.Publisher('/hdmap/node_info', Float32MultiArray, queue_size = 1)
        self.nodeInfoPub = rospy.Publisher('/hdmap/mission_info', Float32MultiArray, queue_size = 1)

    def run(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
