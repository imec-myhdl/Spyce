
from __future__ import division
from builtins import str
from builtins import range
from past.utils import old_div
import sys
from qwt.qt import QtGui, QtCore, uic
from qwt.qt.QtGui import *
from qwt.qt.QtCore import *
import supsictrl.unixsocket as sk

import time
import threading
import os
import socket
import struct
import numpy as np
from qwt import QwtPlot, QwtPlotCurve, QwtPlotGrid

path = os.environ.get('PYSUPSICTRL') + '/'
form_class = uic.loadUiType(path+'BlockEditor/pypltXY.ui')[0]    

class rcvServer(threading.Thread):
    def __init__(self, mainw):
        threading.Thread.__init__(self)
        self.mainw = mainw
        self.N = self.mainw.N
       
    def run(self):
        self.sock, self.connection, self.client_address = sk.open_server(self.mainw.server_address)

        strdata=str(self.N+1)+'d'
        while self.mainw.ServerActive==1:
            data = self.connection.recv(8*(self.N+1))
            if data:
                s = struct.Struct(strdata)
                udata = s.unpack(data)
                for n in range(0,self.N):
                    self.mainw.x[n].append(udata[n+1])
                    if len(self.mainw.x[n]) > self.mainw.Hist:
                          self.mainw.x[n] = self.mainw.x[n][-self.mainw.Hist:]

class dataPlot(QwtPlot):
    def __init__(self, N):
        QwtPlot.__init__(self)
        self.setTitle('X-Y Signals')
        grid = QwtPlotGrid()
        pen = QPen(Qt.black, 0, Qt.DashDotLine)
        grid.setPen(pen)
        grid.attach(self)
                                
class MainWindow(QMainWindow, form_class):
    def __init__(self):
        QMainWindow.__init__(self)
        # Set up the user interface from Designer.
        self.setupUi(self)
        self.connect_widget()
        
        self.ServerActive = 0
        self.server_address = self.edSockName.text().__str__()
        try:
            os.unlink(self.server_address)
        except OSError:
            if os.path.exists(self.server_address):
                raise
        self.colors = ["red", "green", "blue","yellow", "cyan", "magenta", "black", "gray"]
        
    def connect_widget(self):
        self.pbStartServer.clicked.connect(self.pbServerClicked)
        self.edHist.textEdited.connect(self.edHistEdited)
        self.ckAutoscale.stateChanged.connect(self.ckAutoscaleChanged)
        
    def edHistEdited(self, val):
        self.Hist = int(val.__str__())

    def pbServerClicked(self):
        if self.ServerActive == 0:
            self.N = self.sbNsig.value()
            self.Hist = int(self.edHist.text().__str__())
            self.pbStartServer.setText('Stop Server')
            self.ServerActive = 1

            self.plot = dataPlot(self.N)
            self.plot.resize(800, 800)
            self.plot.show()

            self.x = []
            self.c = []
            for n in range(0,self.N):
                self.x.append([])
                
            for n in range(0,int(old_div(self.N,2))):
                cv = QwtPlotCurve()
                pen = QPen(QColor(self.colors[n]))
                cv.setPen(pen)
                cv.setData([],[])
                self.c.append(cv)
                self.c[n].attach(self.plot)
            if not(self.ckAutoscale.isChecked()):
                self.xmin = float(self.edXmin.text().__str__())
                self.xmax = float(self.edXmax.text().__str__())
                self.ymin = float(self.edYmin.text().__str__())
                self.ymax = float(self.edYmax.text().__str__())
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.pltRefresh)
            refTimer = self.sbRefT.value()
            self.timer.start(refTimer)
            self.th = rcvServer(self)
            self.th.start()
        else:
            self.pbStartServer.setText('Start Server')
            self.ServerActive = 0
            self.stopServer()

    def stopServer(self):
        self.timer.stop()
        try:
            sk.close_server(self.th.connection, self.server_address)
        except:
            pass

    def pltRefresh(self):
        for n in range(0,int(old_div(self.N,2))):
            self.c[n].setData(self.x[2*n], self.x[2*n+1])
            
        if not(self.ckAutoscale.isChecked()):
            self.plot.setAxisScale(QwtPlot.xBottom,self.xmin,self.xmax)   
            self.plot.setAxisScale(QwtPlot.yLeft,self.ymin,self.ymax)               
        self.plot.replot()    

    def ckAutoscaleChanged(self,st):
        if st==0:
            self.ckAutoscale.setChecked(False)
            self.label_5.setEnabled(True)
            self.label_6.setEnabled(True)
            self.label_7.setEnabled(True)
            self.label_8.setEnabled(True)
            self.edXmin.setEnabled(True)
            self.edXmax.setEnabled(True)
            self.edYmin.setEnabled(True)
            self.edYmax.setEnabled(True)            
        else:
            self.ckAutoscale.setChecked(True)
            self.label_5.setEnabled(False)
            self.label_6.setEnabled(False)
            self.label_7.setEnabled(False)
            self.label_8.setEnabled(False)
            self.edXmin.setEnabled(False)
            self.edXmax.setEnabled(False)
            self.edYmin.setEnabled(False)
            self.edYmax.setEnabled(False)
            
app = QtGui.QApplication(sys.argv)
frame = MainWindow()
frame.show()
sys.exit(app.exec_())

