# -*- coding: utf-8 -*-
# ARTIV SensorFusion

import rospy
#from tracking_msg.msg import TrackingObject, TrackingObjectArray


import glob, os
from time import sleep
import time
from std_msgs.msg import Int16, Float32MultiArray, Int16MultiArray, MultiArrayDimension
from std_msgs.msg import Int16MultiArray, String
from sensor_msgs.msg import JointState, Image, NavSatFix
import pyqtgraph as pg
from PyQt5.QtWidgets import *
import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtCore import *
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.ticker import MultipleLocator, FuncFormatter
import matplotlib.patches as mpatches
from shapely.geometry import Point, Polygon
import matplotlib
import sys
import numpy as np

from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

import OSMHandler
import map_parser as mission_trigger
sfUI = uic.loadUiType("missionManager.ui")[0]

NODENAME = "missionManager"

class MyArrowItem(pg.ArrowItem):
    def paint(self, p, *args):
        p.translate(-self.boundingRect().center())
        pg.ArrowItem.paint(self, p, *args)


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
        self.setFixedSize(1403, 845)
        self.objPoly = []
        self.plotQueue = 500
        self.plotCnt = 0
        self.center()
        canvasLayout = self.verticalLayout
        self.tableWidget_5.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableWidget_5.setRowCount(24)

        self.footprint = []
        # Matplot init

        self.fig = plt.Figure()
        #self.fig.suptitle('HD MAP', fontsize=16)
        self.fig.patch.set_facecolor('#efefef')

        self.pw1 = pg.PlotWidget()


        #self.view = self.canvas.addViewBox()
        #self.view.setAspectLocked(True)
        #self.view.setRange(QtCore.QRectF(0,0, 100, 100))
        canvasLayout.addWidget(self.pw1)
        pg.setConfigOptions(antialias=True)

        self.pw1.showGrid(x=True, y=True)
        self.pl = self.pw1.plot(pen='g', symbol='o')
        self.guideLinePlot = self.pw1.plot(pen = 'b')
        self.HeadingPlot = self.pw1.plot(pen = 'r')
        self.arrow = 0

        #canvasLayout.addWidget(self.toolbar)

        rospy.init_node(NODENAME, anonymous = True)


        formUpdate = QTimer(self)
        formUpdate.start(10)
        formUpdate.timeout.connect(self.displayUpdate)



        #imgUpdate = QTimer(self)
        #imgUpdate.start(5)
        #imgUpdate.timeout.connect(self.imgdisplay)

        self.pushButton.clicked.connect(self.loadHDMap)

        self.sN = subNode()
        self.sN.start()

        self.mapDefault = 'dgist'

        graphUpdate = QTimer(self)
        graphUpdate.start(500)
        graphUpdate.timeout.connect(self.graphUpdate)

        self.loadHDMap()
        try:
            #self.loadHDMap()
            pass
        except:
            QMessageBox.critical(self, "HD MAP Fail at First", "Failed to load HD Map \nbut you can use whole feature though")

    def graphUpdate(self):
        if self.checkBox.isChecked() :
            #print("hi")

            if len(self.footprint) >= self.plotQueue:
                self.footprint[self.plotCnt % self.plotQueue] = (self.sN.myCoord[0],self.sN.myCoord[1])
            else:
                self.footprint.append((self.sN.myCoord[0],self.sN.myCoord[1]))
            x, y = zip(*self.footprint)


            #self.HeadingPlot.setData(x=[self.sN.myCoord[0]], y=[self.sN.myCoord[1]])]

            if not (self.sN.myCoord[0] == 0 or self.sN.myCoord[1] == 0):
                try:
                    self.pl.setData(x=y[:-1], y=x[:-1])
                    self.pw1.removeItem(self.arrow)
                except:
                    pass

                self.arrow = pg.ArrowItem(pos=(self.sN.myCoord[1], self.sN.myCoord[0]), angle=-90, brush=(0, 255, 0))
                self.pw1.addItem(self.arrow)
            self.plotCnt += 1
            if self.plotCnt <= 1:
                print("Hi i am actiavated")
                self.pw1.disableAutoRange()






    def loadHDMap(self):
        #file_name = "A2_LINK_cut.osm"
        if self.radioButton_2.isChecked():
            self.mapDefault = 'dgist'
        else:
            self.mapDefault = 'k_city'


        print(self.mapDefault)
        #self.osm_loader_list = []
        #osmFiles = './hd_map/' + str(self.mapDefault) + "/" + "B2_SURFACELINEMARK_cut.osm"
        #print(osmFiles)
        self.crosswalksList = mission_trigger.crosswalks_polygons(self.mapDefault)
        try:
            #self.roadList = OSMHandler.nodes(OSMHandler.OSM_data(osmFiles))
            self.crosswalksList = mission_trigger.crosswalks_polygons(self.mapDefault)
            #self.intersectionList = mission_trigger.intersections(self.mapDefault)
            self.protectedareaList = mission_trigger.protected_areas_polygons(self.mapDefault)
            self.guideLineList = mission_trigger.guide_lines_linestrings(self.mapDefault)
            self.missionSectionList = mission_trigger.mission_sections_polygons(self.mapDefault)
        except:
            QMessageBox.critical(self, "HD MAP Fail", "Failed to load HD Map \nbut you can use whole feature though")



        self.processHDMap()

        #print(osm_data)

    def processHDMap(self):
        #self.ax.cla()
        #x, y = zip(*coordRoad)
        #self.ax.scatter(x, y, c='blue', s=1)

        for crossSlice in self.crosswalksList[-300:]:
            x, y = crossSlice.exterior.xy
            #self.ax.fill(x, y, alpha=0.9, fc='red', ec='none')

            pl = self.pw1.plot(pen='r')
            pl.setData(x, y)

        for Slice in self.guideLineList[-500:]:
            #print(Slice.coords.xy)
            x, y = Slice.coords.xy

            pl = self.pw1.plot(pen='b')
            pl.setData(x, y)
            #print(x, y)
            #self.guideLinePlot.setData(x, y)

        for missionSlice in self.missionSectionList:
            x, y = missionSlice.exterior.xy
            #self.ax.fill(x, y, alpha=0.9, fc='red', ec='none')

            pl = self.pw1.plot(pen='w')
            pl.setData(x, y)

        #for Slice in self.protectedareaList:
        #    x, y = Slice.exterior.xy
            #self.ax.fill(x, y, alpha=0.9, fc='yellow', ec='none')

    def zoom_factory(ax,base_scale = 2.):
        def zoom_fun(event):
            # get the current x and y limits
            cur_xlim = self.ax.get_xlim()
            cur_ylim = self.ax.get_ylim()
            cur_xrange = (cur_xlim[1] - cur_xlim[0])*.5
            cur_yrange = (cur_ylim[1] - cur_ylim[0])*.5
            xdata = event.xdata # get event x location
            ydata = event.ydata # get event y location
            if event.button == 'up':
                # deal with zoom in
                scale_factor = 1/base_scale
            elif event.button == 'down':
                # deal with zoom out
                scale_factor = base_scale
            else:
                # deal with something that should never happen
                scale_factor = 1
                print event.button
            # set new limits
            self.ax.set_xlim([xdata - cur_xrange*scale_factor,
                         xdata + cur_xrange*scale_factor])
            self.ax.set_ylim([ydata - cur_yrange*scale_factor,
                         ydata + cur_yrange*scale_factor])
            self.plt.draw() # force re-draw




    def displayUpdate(self):

        self.topicName = ['APS ACT', 'Brake ACT', 'Gear Position', 'Steer', 'E-Stop', 'Auto StandBy', 'APM Switch', 'ASM Switch', 'AGM Switch', 'Override Feedback', 'Turn Signal', 'BPS Pedal', 'APS Pedal', 'Driver Belt', 'Trunk', 'DoorFL', 'DoorFR', 'DoorRL', 'DoorRR', 'Average Speed', 'FL', 'FR', 'RL', 'RR']

        try:
            for i in xrange(0, 24):
                if self.checkBox_6.isChecked():
                    self.tableWidget_5.setItem(0, i*2, QTableWidgetItem(str(self.topicName[i])))

                    self.tableWidget_5.setItem(0, i*2+1, QTableWidgetItem(str(self.sN.infoList[i])))

                    self.lineEdit.setText(str(self.sN.velocity))


        except Exception as ex:

            print(ex)
        pass

    node = 0

    def initPlot(self):
        self.ax.cla()
        self.ax.grid(True, linestyle='--')
        self.ax.axvline(x=1, color='b', linestyle='-', linewidth=0.8, label='lane')
        self.ax.axvline(x=0, color='gray', linestyle='--', linewidth=1)
        self.ax.axvline(x=-1, color='b', linestyle='-', linewidth=0.8)
        self.ax.axis([-10, 10, 40, 0])
        self.ax.invert_yaxis()
        self.ax.minorticks_on()
        self.ax.invert_xaxis()
        self.ax.set_xlabel("y-Position(m)")
        self.ax.set_ylabel("x-Position(m)")
        self.ax.set_facecolor('#efefef')
        pass



class subNode(QThread):
    def __init__(self):
        QThread.__init__(self)
        rospy.Subscriber('/Ioniq_info', Float32MultiArray, self.infoCb)
        rospy.Subscriber('/Joint_state', JointState, self.jointCb)
        rospy.Subscriber('/move_car_info', String, self.moveCb)
        rospy.Subscriber('/gps_fix', NavSatFix, self.navSatCb)
        #rospy.Subscriber('/lidar/tracking_objects', TrackingObjectArray, self.trackCb)
        #rospy.Subscriber('/enetsad/image', Image, self.imageCb)
        #rospy.Subscriber('/enetsad/info', Float32MultiArray, self.enetInfoCb)
        #rospy.Subscriber('/enetsad/cetnerPt', Float32MultiArray, self.enetCenterPt)
        #rospy.Subscriber('/TRT_yolov3/Bbox', Int16MultiArray, self.Bbox_callback)
        #rospy.Subscriber('/TRT_yolov3/result_image', Image, self.imageCb)
        self.infoList = [0] * 24
        self.velocity = 0
        self.moveCarInfo = 0
        self.cvImage = 0
        self.items = []
        self.myCoord = 0, 0

    def run(self):
        rospy.spin()

    def trackCb(self, msg):
        self.items = msg.array
        #for item in msg.array:
        #    print(item.id)

    def navSatCb(self, msg):
        self.myCoord = msg.latitude, msg.longitude

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

        #print(obj_list)

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
