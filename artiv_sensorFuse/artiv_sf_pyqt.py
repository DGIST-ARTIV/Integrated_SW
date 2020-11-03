# ARTIV SensorFusion
# 1010 Pyqt version

import rospy
from tracking_msg.msg import TrackingObject, TrackingObjectArray
from fusion_tracking_msg.msg import FusionTrackingObject, FusionTrackingObjectArray

import os
from time import sleep
import time
from std_msgs.msg import Int16, Float32MultiArray, Int16MultiArray, MultiArrayDimension, Float32
from std_msgs.msg import Int16MultiArray, String
from sensor_msgs.msg import JointState, Image
from cv_bridge import CvBridge
import cv2
import matplotlib.animation
from PyQt5.QtWidgets import *
import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtCore import *
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.ticker import MultipleLocator, FuncFormatter
import matplotlib.patches as mpatches

import matplotlib
import sys
import numpy as np

import pyqtgraph as pg

from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

sfUI = uic.loadUiType("sensorFuse.ui")[0]

NODENAME = "sensorFusion"
bridge = CvBridge()

class obj:
    def __init__(self, xmin, xmax, ymin, ymax, clss, conf):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.clss = get_cls_dict(81)[clss]
        self.conf = conf
    def __repr__(self):
        return "type: " + str(self.clss) + " location: (" + str(self.xmin) + ", " + str(self.ymin) + "), (" + str(self.xmax) + ", " + str(self.xmin) + "), conf: " + str(self.conf)
    def info(self):
        print(self)

COCO_CLASSES_LIST = ['person','bicycle','car','motorbike','aeroplane','bus','train','truck','boat','traffic light','fire hydrant','stop sign','parking meter','bench','bird','cat','dog','horse','sheep','cow','elephant','bear','zebra','giraffe','backpack','umbrella','handbag','tie','suitcase','frisbee','skis','snowboard','sports ball','kite','baseball bat','baseball glove','skateboard','surfboard','tennis racket','bottle','wine glass','cup','fork','knife','spoon','bowl','banana','apple','sandwich','orange','broccoli','carrot','hot dog','pizza','donut','cake','chair','sofa','pottedplant','bed','diningtable','toilet','tvmonitor','laptop','mouse','remote','keyboard','cell phone','microwave','oven','toaster','sink','refrigerator','book','clock','vase','scissors','teddy bear','hair drier','toothbrush', 'Unknown'  , 'Unknown']

def get_cls_dict(category_num):
    """Get the class ID to name translation dictionary."""
    if category_num == 81:
        return {i: n for i, n in enumerate(COCO_CLASSES_LIST)}
    """
    elif category_num == 14:
        return {i: n for i, n in enumerate(K-CITY_CUSTOM_LIST)}
    """




class MyWindow(QMainWindow, sfUI):
    def _int(self, value):
        val = Int16()
        val.data = int(value)
        return val
    def _float(self, value):
        val = Float32()
        val.data = float(value)
        return val

    def __init__(self):
        super(QMainWindow, self).__init__()
        self.setupUi(self)
        self.setFixedSize(1126, 919)
        self.objPoly = []

        canvasLayout = self.verticalLayout
        self.tableWidget_5.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableWidget_5.setRowCount(24)
        self.tableWidget_2.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableWidget_2.setRowCount(5)
        self.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableWidget.setRowCount(4)
        self.comboBox.currentIndexChanged.connect(self.videoFeedSelect)
        self.objPoly = []

        self.horizontalScrollBar.valueChanged.connect(self.cruiseGapBar)
        self.pushButton.clicked.connect(self.sendCruiseSetting)


        px_per_km = 10.0
        tick_step_in_km = 0.1



        # Matplot init
        '''
        self.fig = plt.Figure()
        self.fig.suptitle('Brid Eye View', fontsize=16)
        self.fig.patch.set_facecolor('#efefef')
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(1, 1, 1)
        x, y  = [], []
        self.scat = self.ax.scatter(x, y)
        canvasLayout.addWidget(self.canvas)
        '''
        # PYQt Applied Version
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        self.pw1 = pg.PlotWidget(title="Bird Eye View (LIDAR + VISION)")
        self.pw1.setMouseEnabled(x=False, y=False)
        canvasLayout.addWidget(self.pw1)
        pg.setConfigOptions(antialias=True)
        self.pw1.setWindowTitle('Brid Eye View')
        self.pw1.showGrid(x=True, y=True)
        self.pl = self.pw1.plot(pen='g', symbol='o')
        self.pw1.setXRange(-15, 15, padding=0)
        self.pw1.setYRange(0, 90, padding=0)
        self.guideLinePlot = self.pw1.plot(pen = 'b')
        self.HeadingPlot = self.pw1.plot(pen = 'r')
        self.arrow = 0
        self.scatterplot = 0



        rospy.init_node(NODENAME, anonymous = True)


        formUpdate = QTimer(self)
        formUpdate.start(10)
        formUpdate.timeout.connect(self.displayUpdate)

        graphUpdate = QTimer(self)
        graphUpdate.start(300)
        graphUpdate.timeout.connect(self.graphUpdate)

        #imgUpdate = QTimer(self)
        #imgUpdate.start(5)
        #imgUpdate.timeout.connect(self.imgdisplay)
        self.pN = pubNode()

        self.sN = subNode()
        self.sN.start()

        self.initPlot()

    def sendCruiseSetting(self):
        cruiseGapLevel = self.horizontalScrollBar.value()
        cruiseVelo = self.spinBox.value()
        if self.pushButton.isChecked():
            self.pN.cruiseActive.publish(self._int(1))
            self.pN.cruiseMode.publish(self._int(cruiseGapLevel))
            self.pN.cruiseVelo.publish(self._float(cruiseVelo))
        else:
            self.pN.cruiseActive.publish(self._int(0))






    def cruiseGapBar(self):
        self.lcdNumber_2.display(self.horizontalScrollBar.value())


    def graphUpdate(self):
        if self.checkBox.isChecked() :
            #self.ax.draw_artist(self.ax.patch)

            # set the new data, could be multiple lines too

            #self.axes.draw_artist(self.line)

            if self.sN.items:            # update figure
                pass
                #self.canvas.draw()

        self.label_22.setStyleSheet("color: None;"
              "border-style: None;"
              "border-width: 2px;"
              "border-color: None;"
              "border-radius: 0px")


    def videoFeedSelect(self):
        TopicName = self.comboBox.currentText()
        try:
            self.sN.videoSub.unregister()
        except:
            pass
        #print(TopicName)
        self.sN.videoSub = rospy.Subscriber(TopicName, Image, self.sN.imageCb)

    def imgdisplay(self):
        msg = self.sN.cvImage
        msg = msg[...,::-1].copy()
        qimg = QImage(msg, msg.shape[1], msg.shape[0], QImage.Format_RGB888)
        pix = QPixmap(qimg)
        pix = pix.scaled(391, 201, Qt.KeepAspectRatio)
        self.label_4.setPixmap(pix)


    def displayUpdate(self):

        if self.scatterplot:
            self.pw1.removeItem(self.scatterplot)

        self.topicName = ['APS ACT', 'Brake ACT', 'Gear Position', 'Steer', 'E-Stop', 'Auto StandBy', 'APM Switch', 'ASM Switch', 'AGM Switch', 'Override Feedback', 'Turn Signal', 'BPS Pedal', 'APS Pedal', 'Driver Belt', 'Trunk', 'DoorFL', 'DoorFR', 'DoorRL', 'DoorRR', 'Average Speed', 'FL', 'FR', 'RL', 'RR']

        try:
            for i in xrange(0, 24):
                if self.checkBox_6.isChecked():
                    self.tableWidget_5.setItem(0, i*2, QTableWidgetItem(str(self.topicName[i])))

                    self.tableWidget_5.setItem(0, i*2+1, QTableWidgetItem(str(self.sN.infoList[i])))
            self.lineEdit.setText(str(self.sN.velocity))
        except:
            self.statusBar().showMessage('CAN Data cannot be retreived')

        try: # LDIAR DATA
            self.centerPts = []
            distance = []

            self.lineEdit_3.setText(str(len(self.sN.items)))
            if self.checkBox_2.isChecked(): self.tableWidget_2.setRowCount(len(self.sN.items))
            if len(self.sN.items) == 0: raise Exception
            for idx, tItem in enumerate(self.sN.items):
                #print(tItem)
                sDistance = np.sqrt(np.square(tItem.point.x)+np.square(tItem.point.y))
                distance.append(sDistance)
                state = "moving" if tItem.state else  "stationary"
                if self.checkBox_2.isChecked():
                    self.tableWidget_2.setItem(idx, 0, QTableWidgetItem(str(idx))) # is is gonna be added
                    self.tableWidget_2.setItem(idx, 1, QTableWidgetItem(str(np.round(sDistance, 2))))
                    self.tableWidget_2.setItem(idx, 2, QTableWidgetItem(str(tItem.velocity.x) + ' ,' + str(tItem.velocity.y)))
                    self.tableWidget_2.setItem(idx, 3, QTableWidgetItem(state))
                    self.tableWidget_2.setItem(idx, 4, QTableWidgetItem(str(tItem.type_id)))

                self.objPoly = [(tItem.bev.data[i*2+1], tItem.bev.data[i*2]) for i in xrange(0, 4)] # plot window is inverse axes so, get inversely
                ppy, ppx = zip(*self.objPoly)
                centerPt = ((min(ppy)+max(ppy))/2, (min(ppx)+max(ppx))/2) # in this pt order (y, x)
                self.centerPts.append(centerPt)
                #print(time.time() - start)
        except Exception as ex:
            self.statusBar().showMessage('LIDAR Data cannot be retreived' + str(ex), 5000)

        try: # Vision data
            self.lineEdit_4.setText(str(len(self.sN.obj_list)))
            if self.checkBox_3.isChecked():
                self.tableWidget.setRowCount(len(self.sN.obj_list))
                for idx, Vitem in enumerate(self.sN.obj_list):
                    x, y = (Vitem.xmin + Vitem.xmax)/2, (Vitem.ymin + Vitem.ymax)/2
                    self.tableWidget.setItem(idx, 0, QTableWidgetItem(str(idx))) #ID
                    self.tableWidget.setItem(idx, 1, QTableWidgetItem(str(Vitem.clss))) #Type
                    self.tableWidget.setItem(idx, 2, QTableWidgetItem(str(x) + ', ' +str(y)))
                    self.tableWidget.setItem(idx, 3, QTableWidgetItem("NONE"))
                    self.tableWidget.setItem(idx, 4, QTableWidgetItem("DIST"))
                    self.tableWidget.setItem(idx, 5, QTableWidgetItem(str(Vitem.conf)))


        except: # Vision Data
            self.statusBar().showMessage('vision Data cannot be retreived', 5000)
            pass

        try: # Fusion data
            self.lineEdit_5.setText(str(self.sN.fusionCnt))
            if self.checkBox_4.isChecked():
                self.tableWidget_3.setRowCount(self.sN.fusionCnt)
                temp_X = []
                temp_Y = []
                temp_Dist = []
                for idx, fitem in enumerate(self.sN.fusionData):
                    state = "moving" if fitem.state else  "stationary"
                    self.tableWidget_3.setItem(idx, 0, QTableWidgetItem(str(idx))) #ID TODO
                    #print(len(COCO_CLASSES_LIST))
                    self.tableWidget_3.setItem(idx, 1, QTableWidgetItem(str(get_cls_dict(81)[fitem.type_id]))) #Type
                    self.tableWidget_3.setItem(idx, 2, QTableWidgetItem(str(fitem.point.x) + ', ' +str(fitem.point.y)))
                    self.tableWidget_3.setItem(idx, 3, QTableWidgetItem(state))
                    self.tableWidget_3.setItem(idx, 4, QTableWidgetItem(str(fitem.ttc)))
                    self.tableWidget_3.setItem(idx, 5, QTableWidgetItem(str(fitem.distance.data)))
                    self.tableWidget_3.setItem(idx, 6, QTableWidgetItem(str(fitem.velocity.x) + ', ' + str(fitem.velocity.y)))
                    self.tableWidget_3.setItem(idx, 7, QTableWidgetItem("BEV"))
                    self.tableWidget_3.setItem(idx, 8, QTableWidgetItem(str(fitem.name.data)))

                    if fitem.point.x > 0:
                        temp_X.append(fitem.point.x)
                        temp_Y.append(fitem.point.y * -1) # To Flip Y
                        #temp_Dist.append(int(fitem.distance.data))
                self.scatterplot = pg.ScatterPlotItem(temp_Y, temp_X, symbol='+', color = 'b')
                self.pw1.addItem(self.scatterplot)

                #print(temp_X, temp_Y)
                #self.initPlot()
                #self.ax.scatter(temp_Y, temp_X, s = 15)


        except Exception as ex :
            self.statusBar().showMessage('Fusion Data cannot be retreived  : ' + str(ex), 5000)
            pass

        header2 = self.tableWidget_2.horizontalHeader()
        header2.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header3 = self.tableWidget_3.horizontalHeader()
        header3.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)

        self.lcdNumber.display(self.sN.cruiseData[0])

        if self.sN.cruiseData[1]:
            self.label_22.setStyleSheet("color: red;"
                  "border-style: solid;"
                  "border-width: 6px;"
                  "border-color: #FA8072;"
                  "border-radius: 5px")
            pass

    node = 0


    # Matplot version init
    '''
    def initPlot(self):
        self.ax.cla()
        self.ax.grid(True, linestyle='--')
        self.ax.axvline(x=1, color='b', linestyle='-', linewidth=0.8, label='lane')
        self.ax.axvline(x=0, color='gray', linestyle='--', linewidth=1)
        self.ax.axvline(x=-1, color='b', linestyle='-', linewidth=0.8)
        self.ax.axis([-15, 15, 90, 0])
        self.ax.invert_yaxis()
        self.ax.minorticks_on()
        self.ax.invert_xaxis()
        self.ax.set_xlabel("y-Position(m)")
        self.ax.set_ylabel("x-Position(m)")
        self.ax.set_facecolor('#efefef')
        pass
    '''

    def initPlot(self):
        return
        x = list(xrange(0, 10))
        y = list(xrange(0, 10))
        self.pl.setData(x=y[:-1], y=x[:-1])




class subNode(QThread):
    def __init__(self):
        QThread.__init__(self)
        rospy.Subscriber('/Ioniq_info', Float32MultiArray, self.infoCb)
        rospy.Subscriber('/Joint_state', JointState, self.jointCb)
        rospy.Subscriber('/move_car_info', String, self.moveCb)
        rospy.Subscriber('/lidar/tracking_objects', TrackingObjectArray, self.trackCb)
        #rospy.Subscriber('/enetsad/image', Image, self.imageCb)
        rospy.Subscriber('/enetsad/info', Float32MultiArray, self.enetInfoCb)
        rospy.Subscriber('/enetsad/cetnerPt', Float32MultiArray, self.enetCenterPt)
        rospy.Subscriber('/TRT_yolov3/Bbox', Int16MultiArray, self.Bbox_callback)
        #rospy.Subscriber('/TRT_yolov3/result_image', Image, self.imageCb)
        rospy.Subscriber('/fusion/lidar_camera_test', TrackingObjectArray, self.fusionCb)
        self.videoSub = 0 #rospy.Subscriber('/image', Image, self.imageCb)

        rospy.Subscriber('/smartcruise/gapdist', Float32, self.cruiseGapCb)
        rospy.Subscriber('/smartcruise/event', Int16, self.cruiseEventCb)



        self.infoList = [0] * 24
        self.velocity = 0
        self.moveCarInfo = 0
        self.cvImage = 0
        self.items = []
        self.cruiseData = ['gapDist', 0]

        self.fusionCnt = 0
        self.fusionData = 0

    def run(self):
        rospy.spin()

    def fusionCb(self, msg):
        self.fusionCnt = msg.size
        self.fusionData = msg.array




    def cruiseGapCb(self, msg):
        self.cruiseData[0] = msg.data

    def cruiseEventCb(self, msg):
        self.cruiseData[1] = msg.data

    def trackCb(self, msg):
        self.items = msg.array
        #for item in msg.array:
        #    print(item.id)

    def infoCb(self, msg):
        self.infoList = msg.data
        self.velocity = round(msg.data[20])
        pass

    def jointCb(self, msg):
        self.velocity = msg.velocity[0]
        pass

    def moveCb(self, msg):
        self.moveCarInfo = msg.data
        pass

    def imageCb(self, msg):
        self.cvImage = bridge.imgmsg_to_cv2(msg, "bgr8")
        myWindow.imgdisplay()


    def Bbox_callback(self, msg):
        data = msg.data

        #print(data)
        self.obj_list = []
        if data is not None:
            num_of_obj = len(data)/6
            for i in range(num_of_obj):
                clss = data[6*i]
                conf = data[6*i+1]
                xmin = data[6*i+2]
                xmax = data[6*i+3]
                ymin = data[6*i+4]
                ymax = data[6*i+5]
                temp = obj(xmin, xmax, ymin, ymax, clss, conf)
                self.obj_list.append(temp)

    def enetInfoCb(self, msg):
        self.CurrentlaneIdx = msg.data[1]
        self.laneColorArray = msg.data[2:]



        pass

    def enetCenterPt(self, msg):
        cetnerPt = msg.data
        ptLen = len(centerPt)
        xPt = cetnerPt[:ptLen/2]
        yPt = centerPt[ptLen/2:]

        hi = list(zip(xPt, yPt))
        pass

class pubNode():
    def __init__(self):
        self.cruiseVelo = rospy.Publisher('/smartcruise/cruisevelocity', Float32, queue_size = 1)
        self.cruiseMode = rospy.Publisher('/smartcruise/mode', Int16, queue_size = 1)
        self.cruiseActive = rospy.Publisher('/smartcruise/activate', Int16, queue_size = 1)

    def run(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
