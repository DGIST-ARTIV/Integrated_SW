#!/usr/bin/env python
# dbw_controller
# v2.1 with move_car
#by shinkansan
import rospy

import os
from time import sleep
from std_msgs.msg import Int16, Float32MultiArray
from std_msgs.msg import Int16MultiArray, String
from sensor_msgs.msg import JointState

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
import sys


vtc = uic.loadUiType("vtc.ui")[0]

NODENAME = "dbw_ioniq_controller"
rootname = '/dbw_cmd'

pubAccel = '/Accel'
pubAngular = '/Angular'
pubBrake = '/Brake'
pubSteer = '/Steer'
pubGear = '/Gear'
pubStatus = '/Status'


# TODO reset act value when touch event is over
# ENHANCE add keyboard control feature

class MyWindow(QMainWindow, vtc):
    send_comm_request = pyqtSignal(str)
    proc_kill = pyqtSignal()

    def _int(self, value):
        val = Int16()
        val.data = int(value)
        return val

    def __init__(self):
        super(QMainWindow, self).__init__()
        self.setupUi(self)

        rospy.init_node(NODENAME, anonymous = True)

        self.accelAct.setRange(650, 3700)
        self.accelAct.setSingleStep(200)
        self.accelAct.setValue(650)

        self.brakeAct.setRange(0, 29000)
        self.brakeAct.setSingleStep(1000)
        self.brakeAct.setValue(0)

        #self.label_2.clicked.connect(self.accelAct.setValue(650))
        #self.label_2.clicked.connect(self.brakeAct.setValue(650))

        self.accelAct.valueChanged.connect(self.accelVal)
        self.brakeAct.valueChanged.connect(self.brakeVal)
        self.pushButton_4.clicked.connect(self.emBtn)
        self.horizontalScrollBar.valueChanged.connect(self.steerSet)
        self.horizontalScrollBar_2.valueChanged.connect(self.jointSteer)
        self.pushButton_5.clicked.connect(self.allZero)
        self.pushButton_6.clicked.connect(self.steerZero)
        self.pushButton.clicked.connect(self.publisher)

        self.sN = subNode()
        self.sN.start()

        self.pN = pubNode()
        self.pN.accelPub.publish(self._int(0))
        self.pN.brakePub.publish(self._int(0))
        self.pN.steerPub.publish(self._int(0))
        self.pN.statusPub.publish(self._int(1))

        self.pushButton_7.clicked.connect(self.setP)
        self.pushButton_8.clicked.connect(self.setD)
        self.pushButton_9.clicked.connect(self.setR)

        self.pushButton_10.clicked.connect(self.jointReset)

        self.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableWidget.setRowCount(24)

        self.topicName = ['APS ACT', 'Brake ACT', 'Gear Position', 'Steer', 'E-Stop', 'Auto StandBy', 'APM Switch', 'ASM Switch', 'AGM Switch', 'Override Feedback', 'Turn Signal', 'BPS Pedal', 'APS Pedal', 'Driver Belt', 'Trunk', 'DoorFL', 'DoorFR', 'DoorRL', 'DoorRR', 'Average Speed', 'FL', 'FR', 'RL', 'RR']

        formUpdate = QTimer(self)
        formUpdate.start(300)
        formUpdate.timeout.connect(self.displayUpdate)

        self.realPub = QTimer(self)
        self.realPub.timeout.connect(self.publisher)

        self.checkBox.stateChanged.connect(self.chkPublisher)

        # Cruise Button
        self.pushButton_2.clicked.connect(self.cruiseUp)
        self.pushButton_3.clicked.connect(self.cruiseDown)

        self.pushButton_12.clicked.connect(self.jointEmBtn)
        self.pushButton_11.clicked.connect(self.jointCruise)


        self.pubBool = False

    def cruiseUp(self):
        self.lineEdit.setText(str(float(self.lineEdit.text()) + 5))
    def cruiseDown(self):
        self.lineEdit.setText(str(float(self.lineEdit.text()) -5))

    def jointEmBtn(self):
        self.jointSender(0.0, 0, 0)

    def jointCruise(self):
        self.jointSender(1.0, float(self.lineEdit.text()), 0)

    def jointSteer(self, msg):
        self.jointSender(4.0, -1.0, float(msg))

    def jointReset(self):
        self.jointSender(119.0)


    def jointSender(self, mode=3.0, speed=0.0, steer = 0.0):
        data = Float32MultiArray()
        data.data = [0.0] * 10
        # Ioniq, ERP mode set
        data.data[0] = 0.0


        if mode==0.0:
            print("Emergency activated")
            data.data[1] = 0.0
            data.data[4] = 17000.0 # Brake
        elif mode==1.0:
            print("normal cruise control")
            data.data[1] = 1.0
            data.data[2] = float(speed)
        elif mode==2.0:
            print("steer on cruise mode")
            data.data[1] = 2.0
            data.data[2] = -1.0
            data.data[5] = float(steer)
            data.data[7] = float(self.lineEdit_2.text())
        elif mode == 3.0:
            print("Developer mode")
            data.data[1] = 3.0

        elif mode == 4.0:
            data.data[1] = 4.0
            data.data[2] = -1.0
            data.data[5] = float(steer)
            data.data[7] = float(self.lineEdit_2.text())

        elif mode == 119.0:
            print("Reset joint")
            data = Float32MultiArray()
            data.data = [0]
            data.data[0] = 119.0
        self.pN.jointPub.publish(data)



    def steerZero(self):
        self.horizontalScrollBar.setValue(0)

    def allZero(self):
        self.accelAct.setValue(0)
        self.brakeAct.setValue(0)
        self.pN.statusPub.publish(self._int(1))

    def steerSet(self, steerAngle):
        self.label_8.setText(str(steerAngle))
        self.pN.steerPub.publish(self._int(steerAngle))

    def setP(self):
        self.pN.gearPub.publish(self._int(0))
    def setR(self):
        self.pN.gearPub.publish(self._int(7))
    def setD(self):
        self.pN.gearPub.publish(self._int(5))


    @pyqtSlot()
    def displayUpdate(self):
        try:
            for i in xrange(0, 24):
                self.tableWidget.setItem(1, i*2, QTableWidgetItem(str(self.topicName[i])))

                self.tableWidget.setItem(1, i*2+1, QTableWidgetItem(str(self.sN.infoList[i])))

            self.lcdNumber_3.display(self.sN.velocity)
            #self.label_8.setText(str(self.sN.infoList[3]))

            gearPosition = self.sN.infoList[2]

            if gearPosition == 0:
                self.label_10.setText("P")
            elif gearPosition == 5:
                self.label_10.setText("D")
            elif gearPosition == 6:
                self.label_10.setText("N")
            elif gearPosition == 7:
                self.label_10.setText("R")


        except:
            pass

        if self.sN.moveCarInfo != 0:
            self.textBrowser.setText(str(self.sN.moveCarInfo))

    def accelVal(self):
        #self.brakeAct.setValue(2000)
        if (self.accelAct.value() > 2500):
            buttonReply = QMessageBox.warning(
        self, 'Confirmation', "You are now set Accel to over 2500\n ARE YOU SURE?", QMessageBox.Yes |  QMessageBox.No )
            if buttonReply ==  QMessageBox.No:
                self.accelAct.setValue(2000)


        self.lcdNumber.display(self.accelAct.value())
        self.lcdNumber_2.display(self.brakeAct.value())

        self.publisher()

    def brakeVal(self):
        #self.accelAct.setValue(650)

        self.lcdNumber.display(self.accelAct.value())
        self.lcdNumber_2.display(self.brakeAct.value())

        self.publisher()

    def chkPublisher(self):
        if self.checkBox.isChecked():
            self.realPub.stop()
        else:
            self.realPub.start(1000)


    def publisher(self):
        #print "3"
        self.pN.accelPub.publish(self._int(self.accelAct.value()))
        self.pN.brakePub.publish(self._int(self.brakeAct.value()))
        self.pN.angularPub.publish(self._int(self.lineEdit_2.text()))

        #self.accelAct.setValue(self.accelAct.value()-50)
        #self.brakeAct.setValue(self.brakeAct.value()-500)

    def emBtn(self):
        self.pN.brakePub.publish(self._int(27000))
        rospy.logfatal("Emergency Stop!")

        buttonReply = QMessageBox.warning(
        self, 'EMERGENCY PRESSED', "Heads up! Brace!\n Emergency Override Brake 27000 sended\n\n Press Ok to switch Manual Control")

        self.pN.statusPub.publish(self._int(0))


    def keyPressEvent(self, e):
        print(e.text())

class subNode(QThread):
    def __init__(self):
        QThread.__init__(self)
        rospy.Subscriber('/Ioniq_info', Float32MultiArray, self.infoCb)
        rospy.Subscriber('/Joint_state', JointState, self.jointCb)
        rospy.Subscriber('/move_car_info', String, self.moveCb)
        self.infoList = []
        self.velocity = 0
        self.moveCarInfo = 0

    def run(self):
        while not rospy.core.is_shutdown():
            rospy.rostime.wallsleep(0.5)

    def infoCb(self, msg):
        self.infoList = msg.data
        pass

    def jointCb(self, msg):
        self.velocity = msg.velocity[0]
        pass

    def moveCb(self, msg):
        self.moveCarInfo = msg.data
        pass

class pubNode():
    def __init__(self):
        self.accelPub = rospy.Publisher(rootname+pubAccel, Int16, queue_size = 1)
        self.angularPub = rospy.Publisher(rootname+pubAngular, Int16, queue_size = 1)
        self.brakePub = rospy.Publisher(rootname+pubBrake, Int16, queue_size = 1)
        self.steerPub = rospy.Publisher(rootname+pubSteer, Int16, queue_size = 1)
        self.gearPub = rospy.Publisher(rootname+pubGear, Int16, queue_size = 1)
        self.statusPub = rospy.Publisher(rootname+pubStatus, Int16, queue_size = 1)
        self.jointPub = rospy.Publisher('/move_car', Float32MultiArray, queue_size = 1)

    def run(self):
        pass



if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
