import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
import PyQt5
from PyQt5 import *
import PyQt5.QtCore as C
import rclpy
from rcl_interfaces.msg import Log
from PyQt5.QtWidgets import * #PyQt import
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtMultimedia import QMediaPlaylist, QMediaContent, QMediaPlayer
from PyQt5 import QtMultimedia
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl
import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore, QtGui
import datetime
import threading
import time


form_window = uic.loadUiType("logalert.ui")[0]
alert_window = uic.loadUiType("alertScreen.ui")[0]
FATAL_window = uic.loadUiType("fatalScreen.ui")[0]

header_serverity = 0
header_comment = 1
header_time = 2
header_loc = 3
blank_toggle = 1
aSshow = 1
fSshow = 1
coppinShow = 1

class Stack(list):
    push = list.append

    def is_empty(self):
        if not self:
            return True
        else:
            return False

    def peek(self):
        return self[-1]
fatalList = Stack()
'''TODO
class alertSound(QThread):
    def __init__(self):
        super().__init__()

    def run(self):
'''

class coppin(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        p =self.palette()
        p.setColor(QPalette.Window, Qt.black)
        self.setPalette(p)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.center()
        self.init_ui()
        self.play()

    def center(self): #for load ui at center of screen
        frameGm = self.frameGeometry()
        screen = PyQt5.QtWidgets.QApplication.desktop().screenNumber(PyQt5.QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = PyQt5.QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def init_ui(self):

        #create media player object
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        videowidget = QVideoWidget()
        self.mediaPlayer.setVideoOutput(videowidget)
        vboxLayout = QVBoxLayout()
        vboxLayout.addWidget(videowidget)

    def play(self):
        # This is fake
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(os.path.join(os.getcwd(), "warning3.mp4"))))
        self.mediaPlayer.play()


class alertScreen(QMainWindow, alert_window):

    def center(self): #for load ui at center of screen
        frameGm = self.frameGeometry()
        screen = PyQt5.QtWidgets.QApplication.desktop().screenNumber(PyQt5.QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = PyQt5.QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def location_on_the_screen(self):
        screen = QDesktopWidget().screenGeometry()
        widget = self.geometry()
        x = screen.width() - widget.width()
        #y = screen.height() - widget.height()
        y = 30# widget.height()
        self.move(x, y)


    def __init__(self):
        super().__init__()
        self.setupUi(self)
        #self.center()
        self.location_on_the_screen()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.pushButton.clicked.connect(self._exit)

        self.playlist = QMediaPlaylist()
        url = C.QUrl.fromLocalFile(os.path.join(os.getcwd(), "./ChargingStarted_Calm.ogg"))
        #url = C.QUrl.fromLocalFile(os.path.join(os.getcwd(), "./Water_Protection.ogg"))
        url = C.QUrl.fromLocalFile(os.path.join(os.getcwd(), "./TW_Silent_mode_off_Calm.ogg"))
        self.playlist.addMedia(QMediaContent(url))

        self.timeout = 2500


        self.setStyleSheet("background-color:  #efefef;"
                      "border-style: solid;"
                      "border-width: 9px;"
                      "border-color: #ff4444;"
                      "border-radius: 3px")

        self.label_2.setStyleSheet("color: black;"
                      "border-style: None;"
                      "border-width: 2px;"
                      "border-color: #FA8072;"
                      "border-radius: 3px")

        self.label.setStyleSheet("color: black;"
                      "border-style: None;"
                      "border-width: 2px;"
                      "border-color: #FA8072;"
                      "border-radius: 3px")

        self.listWidget.setStyleSheet("color: balck;"
                      "border-style: None;"
                      "border-width: 2px;"
                      "border-color: #000000;"
                      "border-radius: 3px")
        self.pushButton.setStyleSheet("color: balck;"
                      "border-style: solid;"
                      "border-width: 2px;"
                      "border-color: #000000;"
                      "border-radius: 3px")

        timer = QtCore.QTimer(self)
        timer.setInterval(400)
        timer.timeout.connect(self.blank)
        timer.start()

        self.alertSound = QtCore.QTimer(self)
        self.doAlert()
        self.alertSound.timeout.connect(self.doAlert)
        self.alertSound.start()
        self.alertSound.setInterval(self.timeout)

    def openCoppin(self):
        pass


    def blank(self):
        global blank_toggle
        if(blank_toggle):
            self.setStyleSheet("background-color:  #efefef;"
                          "border-style: solid;"
                          "border-width: 20px;"
                          "border-color: #2c698d;"
                          "border-radius: 2px")
            blank_toggle = 0
        else:
            self.setStyleSheet("background-color:  #efefef;"
                          "border-style: solid;"
                          "border-width: 20px;"
                          "border-color: #bae8e8;"
                          "border-radius: 2px")
            blank_toggle = 1
        self.updateList()

    def doAlert(self):
        self.player = QMediaPlayer()
        self.player.setPlaylist(self.playlist)
        self.player.play()
        #if self.timeout > 300 : self.timeout -= 50
        self.alertSound.setInterval(self.timeout)


    def updateList(self):
        global fatalList, coppinShow
        if fatalList:
            if fatalList.peek()[2] != "WARNING": return # alert : pass the FATAL
            item = fatalList.pop()
            self.listWidget.addItem(str(item[1]) + " : " + str(item[3]))
        if self.listWidget.count() > 4 and coppinShow == 1:
            self.openCoppin()
            coppinShow = 0


    def _exit(self):
        global aSshow

        aSshow = 1
        logAlert_form.alarmTimeout()
        self.player.stop()
        self.alertSound.stop()
        self.hide()

class FATALScreen(QMainWindow, FATAL_window):

    def center(self): #for load ui at center of screen
        frameGm = self.frameGeometry()
        screen = PyQt5.QtWidgets.QApplication.desktop().screenNumber(PyQt5.QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = PyQt5.QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def location_on_the_screen(self):
        screen = QDesktopWidget().screenGeometry()
        widget = self.geometry()
        x = screen.width() - widget.width()
        #y = screen.height() - widget.height()
        y = 170# widget.height()
        self.move(x, y)


    def __init__(self):
        super().__init__()
        self.setupUi(self)
        #self.center()
        self.location_on_the_screen()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.pushButton.clicked.connect(self._exit)

        self.playlist = QMediaPlaylist()
        #url = C.QUrl.fromLocalFile(os.path.join(os.getcwd(), "./ChargingStarted_Calm.ogg"))
        #url = C.QUrl.fromLocalFile(os.path.join(os.getcwd(), "./Water_Protection.ogg"))
        url = C.QUrl.fromLocalFile(os.path.join(os.getcwd(), "./Alert_on_call.ogg"))
        self.playlist.addMedia(QMediaContent(url))

        self.timeout = 1000


        self.setStyleSheet("background-color:  #efefef;"
                      "border-style: solid;"
                      "border-width: 9px;"
                      "border-color: #ff4444;"
                      "border-radius: 3px")

        self.label_2.setStyleSheet("color: black;"
                      "border-style: None;"
                      "border-width: 2px;"
                      "border-color: #FA8072;"
                      "border-radius: 3px")

        self.label.setStyleSheet("color: black;"
                      "border-style: None;"
                      "border-width: 2px;"
                      "border-color: #FA8072;"
                      "border-radius: 3px")

        self.listWidget.setStyleSheet("color: balck;"
                      "border-style: None;"
                      "border-width: 2px;"
                      "border-color: #000000;"
                      "border-radius: 3px")
        self.pushButton.setStyleSheet("color: balck;"
                      "border-style: solid;"
                      "border-width: 2px;"
                      "border-color: #000000;"
                      "border-radius: 3px")

        timer = QtCore.QTimer(self)
        timer.setInterval(100)
        timer.timeout.connect(self.blank)
        timer.start()

        self.alertSound = QtCore.QTimer(self)
        self.doAlert()
        self.alertSound.timeout.connect(self.doAlert)
        self.alertSound.start()
        self.alertSound.setInterval(self.timeout)

    def openCoppin(self):
        pass


    def blank(self):
        global blank_toggle
        if(blank_toggle):
            self.setStyleSheet("background-color:  #efefef;"
                          "border-style: solid;"
                          "border-width: 20px;"
                          "border-color: #ff4444;"
                          "border-radius: 2px")
            blank_toggle = 0
        else:
            self.setStyleSheet("background-color:  #efefef;"
                          "border-style: solid;"
                          "border-width: 20px;"
                          "border-color: #ffbb33;"
                          "border-radius: 2px")
            blank_toggle = 1
        self.updateList()

    def doAlert(self):
        self.player = QMediaPlayer()
        self.player.setPlaylist(self.playlist)
        self.player.play()
        #if self.timeout > 300 : self.timeout -= 50
        self.alertSound.setInterval(self.timeout)


    def updateList(self):
        global fatalList, coppinShow
        if fatalList:
            if fatalList.peek()[2] == "WARNING" : return
            item = fatalList.pop()
            self.listWidget.addItem(str(item[1]) + " : " + str(item[3]))
        if self.listWidget.count() > 4 and coppinShow == 1:
            self.openCoppin()
            coppinShow = 0


    def _exit(self):
        global fSshow
        fSshow = 1
        logAlert_form.alarmTimeout()
        self.player.stop()
        self.alertSound.stop()
        self.hide()


class logAlert(QMainWindow, form_window):
    def center(self): #for load ui at center of screen
        frameGm = self.frameGeometry()
        screen = PyQt5.QtWidgets.QApplication.desktop().screenNumber(PyQt5.QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = PyQt5.QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())
        self.dataPop = []

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.center()

        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setHorizontalHeaderLabels(['내용', '심각도', '발생', '시간'])

        self.tableWidget.setColumnWidth(0, 80)


        self.rosSub_class = rosSub()
        self.rosSub_class.start()
        self.rosSub_class.data.connect(self.logUpdate)
        self.rosSub_class.data.connect(self.showAlert)

        displayUp = QTimer(self)
        displayUp.start(500)
        displayUp.timeout.connect(self.displayUpdate)

        self.pushButton.clicked.connect(self.snoozeAlarm)
        self.snoozeBool = False

        '''
        playlist = QMediaPlaylist()
        print(os.path.join(os.getcwd(), "warning_fx.mp3"))
        url = QUrl.fromLocalFile(os.path.join(os.getcwd(), "warning_fx.mp3"))
        playlist.addMedia(QMediaContent(url))
        #playlist.setPlaybackMode(QMediaPlaylist.Loop)

        player = QMediaPlayer()
        player.setVolume(100)
        player.setPlaylist(playlist)

        self.pushButton_2.clicked.connect(player.play)

        player.play()
        '''
        filename = 'warning_fx.mp3'
        fullpath = QtCore.QDir.current().absoluteFilePath(filename)
        media = QtCore.QUrl.fromLocalFile(fullpath)
        content = QtMultimedia.QMediaContent(media)
        player = QtMultimedia.QMediaPlayer()
        player.setMedia(content)
        player.play()

        #header_item = QTableWidgetItem("추가")
        #header_item.setBackground(Qt.red) # 헤더 배경색 설정 --> app.setStyle() 설정해야만 작동한다. self.table.setHorizontalHeaderItem(2, header_item)
        #self.tableWidget.setHorizontalHeaderItem(2, header_item)

    def displayUpdate(self):
        for its in self.dataPop:
            time.sleep(0.001)
            self.addRowandSet(its)
        self.dataPop = []

    def logUpdate(self, _data):
        #print(self.dataPop)
        try:
            if self.dataPop[-1][0] == 16 or self.dataPop[-1][0] == 50 or self.dataPop[-1][0] == 30 or self.dataPop[-1][0] == 8  or self.dataPop[-1][0] == 40 or self.dataPop[-1][0] == 4 and self.dataPop[-1][3] == _data[3]:
                print("Skip same Warn", self.dataPop[-1][2], _data[3], _data[2])
                return
        except:
            pass
        self.dataPop.append(_data)

    def putIcon(self, severity):
        iconList = ['SP_MessageBoxCritical',
                    'SP_MessageBoxInformation',
                    'SP_MessageBoxQuestion',
                    'SP_MessageBoxWarning',
                    ]
        if severity == 1 or severity == 10:
            #Debug
            return self.style().standardIcon(getattr(QStyle, iconList[2])), "DEBUG", Qt.white
            pass
        elif severity == 2 or severity == 20:
            #INFO
            return self.style().standardIcon(getattr(QStyle, iconList[1])), "INFO", Qt.white
            pass
        elif severity == 4 or severity == 30:
            #WARN
            return self.style().standardIcon(getattr(QStyle, iconList[3])), "WARNING", Qt.yellow
            pass
        elif severity == 8 or severity == 40:
            #ERROR
            return self.style().standardIcon(getattr(QStyle, iconList[0])), "ERROR", Qt.darkRed
            pass
        elif severity == 16 or severity == 50:
            #FATAL
            return  self.style().standardIcon(getattr(QStyle, iconList[0])), "FATAL", Qt.magenta
            pass
        elif severity == 0:
            #UNSET
            return ""
            pass

    def snoozeAlarm(self):

        if self.pushButton.text() == "Alarm : ON":
            self.pushButton.setText("Alarm : OFF")
            self.snoozeBool = True
        else:
            self.pushButton.setText("Alarm : ON")
            self.snoozeBool = False



    def offAlarm(self):
        self.pushButton.setText("Alarm : OFF")
        self.snoozeBool = True

    def onAlarm(self):
        self.pushButton.setText("Alarm : ON")
        self.snoozeBool = False
    def alarmTimeout(self):

        if self.pushButton.text == "Alarm : OFF":
            return
        self.offAlarm()
        QTimer.singleShot(10000, lambda: self.onAlarm())




    def showAlert(self, _data):
        if _data[0] == 16 or _data[0] == 50:
            _data[2] = "FATAL"
        elif _data[0] == 8 or _data[0] == 40:
            _data[2] = "ERROR"
        elif _data[0] == 4 or _data[0] == 30:
            _data[2] = "WARNING"

        if not self.snoozeBool:
            #print(_data[2], _data[0])
            if _data[2] == "FATAL" or _data[2] == "ERROR":
                global fSshow
                self.fatalCollector(_data)
                if fSshow:

                    self.aS2 = FATALScreen()
                    self.aS2.show()
                    fSshow = 0

            if _data[2] == "WARNING":
                global aSshow
                self.fatalCollector(_data)
                if aSshow:

                    self.aS = alertScreen()
                    self.aS.show()

                    aSshow = 0
    def addRowandSet(self, _data):
        # fileter for passing "INFO"

        global aSshow
        global fSshow

        serverity = self.putIcon(_data[0])[1]
        _data[2] = serverity

        if _data[2] == "INFO":
            return


        row_count = self.tableWidget.rowCount()
        self.tableWidget.setRowCount(row_count+1)



        meesage = QTableWidgetItem(_data[1])
        meesage.setIcon(self.putIcon(_data[0])[0])
        serverity = QTableWidgetItem(_data[2])
        serverity.setBackground(self.putIcon(_data[0])[2])
        self.tableWidget.setItem(row_count, 0, meesage)
        self.tableWidget.setItem(row_count, 1, serverity)
        self.tableWidget.setItem(row_count, 2, QTableWidgetItem(_data[3]))
        self.tableWidget.setItem(row_count, 3, QTableWidgetItem(_data[4]))


        #
        #self.tableWidget.setColumnWidth(1, 380)
        #self.tableWidget.setColumnWidth(2, 150)
        #self.tableWidget.setColumnWidth(3, 320)
        header = self.tableWidget.horizontalHeader()
        #header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        self.tableWidget.setColumnWidth(0, 300)
        self.tableWidget.scrollToBottom()

    def fatalCollector(self, data):
        global fatalList
        fatalList.append(data)



class rosSub(QThread):
    data = pyqtSignal(list)
    def __init__(self):
        super().__init__()
        rclpy.init()
        self.node = rclpy.create_node("watch_Dog")

    def run(self):
        self.node.create_subscription(Log, '/rosout', self.callback)

        while rclpy.ok():
            rclpy.spin_once(self.node)
            time.sleep(0.01)



    def callback(self, msg):

        temp_data = [None] * 5
        temp_data[0] = msg.level
        temp_data[1] = msg.msg
        #temp_data[2] = str(msg.stamp)
        temp_data[4] = str(datetime.datetime.now())[5:]
        temp_data[3] = str(msg.name) + ":" +str(msg.line)

        self.data.emit(temp_data)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    logAlert_form = logAlert()
    logAlert_form.show()
    app.exec_()
