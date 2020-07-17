#!/usr/bin/env python
import rospy

import os
from time import sleep
from std_msgs.msg import Int16, Float32MultiArray
from sensor_msgs.msg import JointState

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
import sys


vtc = uic.loadUiType("vtc.ui")[0]

NODENAME = "vehicle_controller"
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

        self.brakeAct.setRange(2000, 25000)
        self.brakeAct.setSingleStep(1000)
        self.brakeAct.setValue(2000)

        #self.label_2.clicked.connect(self.accelAct.setValue(650))
        #self.label_2.clicked.connect(self.brakeAct.setValue(650))

        self.accelAct.valueChanged.connect(self.accelVal)
        self.brakeAct.valueChanged.connect(self.brakeVal)
        self.pushButton_4.clicked.connect(self.emBtn)
        self.horizontalScrollBar.valueChanged.connect(self.steerSet)
        self.pushButton_5.clicked.connect(self.allZero)
        self.pushButton_6.clicked.connect(self.steerZero)

        self.sN = subNode()
        self.sN.start()

        self.pN = pubNode()
        self.pN.accelPub.publish(self._int(0))
        self.pN.brakePub.publish(self._int(0))
        self.pN.steerPub.publish(self._int(0))
        self.pN.statusPub.publish(self._int(0))

        self.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableWidget.setRowCount(24)

        self.topicName = ['APS ACT', 'Brake ACT', 'Gear Position', 'Steer', 'E-Stop', 'Auto StandBy', 'APM Switch', 'ASM Switch', 'AGM Switch', 'Override Feedback', 'Turn Signal', 'BPS Pedal', 'APS Pedal', 'Driver Belt', 'Trunk', 'DoorFL', 'DoorFR', 'DoorRL', 'DoorRR', 'Average Speed', 'FL', 'FR', 'RL', 'RR']

        formUpdate = QTimer(self)
        formUpdate.start(300)
        formUpdate.timeout.connect(self.displayUpdate)

        self.realPub = QTimer(self)
        self.realPub.timeout.connect(self.publisher)

        self.checkBox.stateChanged.connect(self.chkPublisher)


        self.pubBool = False

    def steerZero(self):
        self.horizontalScrollBar.setValue(0)

    def allZero(self):
        self.accelAct.setValue(0)
        self.brakeAct.setValue(0)

    def steerSet(self, steerAngle):
        self.label_8.setText(str(steerAngle))
        self.pN.steerPub.publish(self._int(steerAngle))


    @pyqtSlot()
    def displayUpdate(self):
        try:
            for i in xrange(0, 24):
                self.tableWidget.setItem(1, i*2, QTableWidgetItem(str(self.topicName[i])))

                self.tableWidget.setItem(1, i*2+1, QTableWidgetItem(str(self.sN.infoList[i])))

            self.lcdNumber_3.display(self.sN.velocity)
            #self.label_8.setText(str(self.sN.infoList[3]))
        except:
            pass

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

        #self.accelAct.setValue(self.accelAct.value()-50)
        #self.brakeAct.setValue(self.brakeAct.value()-500)

    def emBtn(self):
        self.pN.brakePub.publish(self._int(14000))
        rospy.logfatal("Emergency Stop!")

        buttonReply = QMessageBox.warning(
        self, 'EMERGENCY PRESSED', "Heads up! Brace!\n Emergency Override Brake 14000 sended\n\n Press Ok to switch Manual Control")

        self.pN.statusPub.publish(self._int(1))


    def keyPressEvent(self, e):
        print(e.text())

class subNode(QThread):
    def __init__(self):
        QThread.__init__(self)
        rospy.Subscriber('/Ioniq_info', Float32MultiArray, self.infoCb)
        rospy.Subscriber('/Joint_state', JointState, self.jointCb)
        self.infoList = []
        self.velocity = 0

    def run(self):
        while not rospy.core.is_shutdown():
            rospy.rostime.wallsleep(0.5)

    def infoCb(self, msg):
        self.infoList = msg.data
        pass

    def jointCb(self, msg):
        self.velocity = msg.velocity[0]
        pass

class pubNode():
    def __init__(self):
        self.accelPub = rospy.Publisher(rootname+pubAccel, Int16, queue_size = 1)
        self.angularPub = rospy.Publisher(rootname+pubAngular, Int16, queue_size = 1)
        self.brakePub = rospy.Publisher(rootname+pubBrake, Int16, queue_size = 1)
        self.steerPub = rospy.Publisher(rootname+pubSteer, Int16, queue_size = 1)
        self.gearPub = rospy.Publisher(rootname+pubGear, Int16, queue_size = 1)
        self.statusPub = rospy.Publisher(rootname+pubStatus, Int16, queue_size = 1)

    def run(self):
        pass



if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
