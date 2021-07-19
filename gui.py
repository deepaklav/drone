import os


import sys
from PyQt5 import *
from PyQt5.QtGui import * 
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
#import RPi.GPIO as gpio
#gpio.setmode(gpio.BCM)
from random import randint
import pyqtgraph as pg
from pyqtgraph import PlotWidget, plot

class Signal(QObject):
    signal_drag = pyqtSignal()

###
'''

class GPIO_BIND(QThread):
    def __init__(self):
        gpio.setup(15,gpio.OUT)

    GPIO.output(14,GPIO.HIGH)
    self.pwm_1 = GPIO.PWM(13, 50)  


'''
###


class Temp(QThread):
    def __init__(self):
        print("thread_start")



class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ax = 10
        self.yx = 10
        self.row = 320
        self.col = 100
        self.z = []
        self.Dragger_visible = 0
        self.InitUI()

    def InitUI(self):
        self.setWindowTitle("in_process")
        self.setGeometry(self.ax,self.yx,self.row,self.col)
        self.widget = QWidget()
        windowLayout = QVBoxLayout()
        windowLayout.stretch(1)
        oImage = QImage("backup.jpg")
        sImage = oImage.scaled(QSize(2000,950))                   # resize Image to widgets size
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))                        
        self.setPalette(palette)
        self.graphWidget = pg.PlotWidget()
        self.graph_plot()
        self.CreateUI()

        windowLayout.addWidget(self.horizontalGroupBox)
        self.widget.setLayout(windowLayout)
        self.setCentralWidget(self.widget)
        self.showFullScreen()   

    def CreateUI(self):

        self.horizontalGroupBox = QGroupBox() 
        self.grid = QGridLayout()
        self.grid.setColumnStretch(6, 9)
        self.grid.setColumnStretch(6, 9)
        self.grid.setSpacing(1)
        self.Indication = QLabel(self)
        self.Indication.setText("ON/OFF")
        self.Indication.setStyleSheet("color:white")
        
        self.empty_label = QLabel(self)
        self.empty_label.setText("")
        
        self.ON_OFF = QPushButton(self)
        self.ShutDwn = QPushButton(self)
        self.ShutDwn.setText("Power-Off")
        self.ShutDwn.clicked.connect(self.os_shutdown)

        self.RIGHT = QPushButton(self)
        self.RIGHT.setText("R")
        
        self.LEFT = QPushButton(self)
        self.LEFT.setText("L")
        self.LEFT.setCheckable(True)
 
        self.UP = QPushButton(self)
        self.UP.setText("U")

        self.DOWN = QPushButton(self)
        self.DOWN.setText("D")

        self.OBject = QLabel(self)
        self.OBject.setText("OBSTACLE : ")
        self.OBject.setStyleSheet("color:white")

        self.ON_OFF.setStyleSheet("background-color:red")
        self.ON_OFF.setText("START")
        self.ON_OFF.clicked.connect(self.on_stop)
        self.ON_OFF.clicked.connect(self.Dragger_wid)
        self.ON_OFF.clicked.connect(self.camera_init)
        print(">>>off_chart>>>")
        self.view = QCameraViewfinder()

        self.grid.addWidget(self.Indication,0,0)
        self.grid.addWidget(self.ON_OFF,2,1)
        self.grid.addWidget(self.ShutDwn,0,1)
        self.grid.addWidget(self.UP,4,1)
        self.grid.addWidget(self.DOWN,6,1)
        self.grid.addWidget(self.LEFT,5,0)
        self.grid.addWidget(self.RIGHT,5,2)
        self.grid.addWidget(self.view,1,9,8,9)
        self.grid.addWidget(self.ShutDwn,2,0)
        self.grid.addWidget(self.empty_label,3,0)
        self.grid.addWidget(self.OBject,8,8)
        
        self.grid.addWidget(self.empty_label,5,3)

        
        
        ### set button as repeat mode ####
        self.RIGHT.setAutoRepeat(True)
        self.RIGHT.setAutoRepeatInterval(1)
        self.LEFT.setAutoRepeat(True)
        self.LEFT.setAutoRepeatInterval(1)
        self.UP.setAutoRepeat(True)
        self.UP.setAutoRepeatInterval(2)
        self.DOWN.setAutoRepeat(True)
        self.DOWN.setAutoRepeatInterval(2)

        ### changing button color ####
        self.RIGHT.clicked.connect(self.button_color_up)
        self.LEFT.clicked.connect(self.button_color_up)
        self.UP.clicked.connect(self.button_color_up)
        self.DOWN.clicked.connect(self.button_color_up)
        self.graphWidget.hide()  
        self.graphWidget.setBackground('#192b41')
        self.grid.addWidget(self.graphWidget,9,9)
        

        self.time = QTimer(self)
        self.time.setInterval(100)
        self.time.timeout.connect(self.update_plot_data)

        self.horizontalGroupBox.setLayout(self.grid)
    
    def Dragger_wid(self):                              #dailbox for led pwm
        self.Dragger = QDial(self)
        self.Dragger.setStyleSheet("background-color:#8E947C")
        self.Dragger.setRange(0,99)
        self.Dragger.valueChanged.connect(self.Dragger_value)
        self.grid.addWidget(self.Dragger,5,1)

    def on_stop(self):

        self.ON_OFF_2 = QPushButton(self)
 #       self.ON_OFF_2.setCheckable(True)
        self.ON_OFF_2.setText("STOP")
        self.ON_OFF_2.setStyleSheet("background-color:green")
        self.ON_OFF_2.setVisible(True)
        if self.Dragger_visible == 1:
            self.Dragger.show()
        self.graphWidget.show()
        self.time.start()    
        self.graph_visible = 1    
        print(">>>STOP_ACTION>>>")
        self.ON_OFF_2.clicked.connect(self.on_start)
        self.ON_OFF_2.clicked.connect(self.camera_close)

        self.grid.addWidget(self.ON_OFF_2,2,1)
    def on_start(self):
        
        self.Dragger.hide()
    #    if self.graph_visible == 1:
    #        self.graphWidget.hide()
        self.Dragger_visible = 1
        self.time.stop()
        print(">>>START_ACTION>>>")
        self.ON_OFF_2.setVisible(False)

    def Dragger_value(self,value):
        global Dragger_value                    #pass to pwm pin as duty cycle
        print(">>>value :",value)

    def camera_init(self):                        #camera initilization
        self.camera_search = QCameraInfo.availableCameras()
        if not self.camera_search:
            pass

        self.camera_open(0)                     #use argument when using multiple camera

    def camera_open(self,i):
        self.camera = QCamera(self.camera_search[i])                #for second camera use i
        self.camera.setViewfinder(self.view)
        self.camera.setCaptureMode(QCamera.CaptureStillImage)
        self.camera_show()

    def camera_show(self):                              #start
        self.view.show()
        self.camera.start()   
    def camera_close(self):                             #stop
        self.camera.stop()
  #      self.view.hide()
        
    def button_color_up(self):
        sender =self.sender()
        print(sender.text())
        self.connect  = sender.text()
        if self.connect == "U":
            self.UP_color()    
        if self.connect == "D":
            self.DOWN_color() 
        if self.connect == "R":
            self.RIGHT_color()
        if self.connect == "L":
            self.LEFT_color()
             


    def UP_color(self):
        self.UP.setStyleSheet("background-color:blue")
        self.DOWN.setStyleSheet("background-color:white")
        self.RIGHT.setStyleSheet("background-color:white")
        self.LEFT.setStyleSheet("background-color:white")

    def DOWN_color(self):
        self.UP.setStyleSheet("background-color:white")
        self.DOWN.setStyleSheet("background-color:blue")
        self.RIGHT.setStyleSheet("background-color:white")
        self.LEFT.setStyleSheet("background-color:white")

    def RIGHT_color(self):
        self.UP.setStyleSheet("background-color:white")
        self.DOWN.setStyleSheet("background-color:white")
        self.RIGHT.setStyleSheet("background-color:blue")
        self.LEFT.setStyleSheet("background-color:white")

    def LEFT_color(self):
        self.UP.setStyleSheet("background-color:white")
        self.DOWN.setStyleSheet("background-color:white")
        self.RIGHT.setStyleSheet("background-color:white")
        self.LEFT.setStyleSheet("background-color:blue")

    def graph_plot(self):
        pen = pg.mkPen(color=(255, 0, 0))
        self.x = list(range(100))  # 100 time points
        self.y = [randint(0,100) for _ in range(100)]  
        

        self.data_line =  self.graphWidget.plot(self.x, self.y, pen=pen)
    def update_plot_data(self):
      
      
        self.z.append(randint(0,100))
        value = int(self.z[-1])  #     change sensor value to value
        self.x = self.x[1:]  # Remove the first y element.
        self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.
        self.y = self.y[1:] 
        self.y.append(value)  # use sensor value in y list 

        self.data_line.setData(self.x, self.y)  # Update the data.    

    def os_shutdown(self):
        os.system("shutdown now")    
            

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
