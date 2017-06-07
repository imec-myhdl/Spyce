#!/usr/bin/python

import sys
import os

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
form_class = uic.loadUiType(path+'BlockEditor/pyplt.ui')[0]    

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

                self.mainw.timebase.append(udata[0]);
                if len(self.mainw.timebase) > self.mainw.Hist:
                    self.mainw.timebase = self.mainw.timebase[-self.mainw.Hist:]
                for n in range(0,self.N):
                    self.mainw.x[n].append(udata[n+1])
                    if len(self.mainw.x[n]) > self.mainw.Hist:
                        self.mainw.x[n] = self.mainw.x[n][-self.mainw.Hist:]

class dataPlot(QwtPlot):
    def __init__(self, N):
        QwtPlot.__init__(self)
        self.setTitle('Time signals')
        grid = QwtPlotGrid()
        pen = QPen(Qt.black, 0, Qt.DashDotLine)
        grid.setPen(pen)
        grid.attach(self)
                                
class MainWindow(QMainWindow, form_class):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
          
        self.connect_widget()

        self.ServerActive = 0
        self.server_address = self.edSockName.text().__str__()
        self.colors = ["red", "green", "blue","yellow", "cyan", "magenta", "black", "gray"]

    def connect_widget(self):
        self.pbStartServer.clicked.connect(self.pbServerClicked)
        self.edHist.textEdited.connect(self.edHistEdited)

    def edHistEdited(self, val):
        self.Hist = int(val.__str__())
        
    def pbServerClicked(self):
        if self.ServerActive == 0:
            self.N = self.sbNsig.value()
            self.Hist = int(self.edHist.text().__str__())
            self.pbStartServer.setText('Stop Server')
            self.ServerActive = 1
            
            self.plot = dataPlot(self.N)
            self.plot.resize(800, 500)
            self.plot.show()
            
            self.timebase = []
            self.x = []
            self.c = []
            for n in range(0, self.N):
                self.x.append([])
                cv = QwtPlotCurve()
                pen = QPen(QColor(self.colors[n]))
                cv.setPen(pen)
                cv.setData([],[])
                self.c.append(cv)
                self.c[n].attach(self.plot)
                
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
        if len(self.x[0]) > self.Hist:
            for n in range(0,self.N):
                self.x[n] = self.x[n][-self.Hist:]
            self.timebase = self.timebase[-self.Hist:]
        if(len(self.timebase)>2):
            self.plot.setAxisScale(QwtPlot.xBottom,self.timebase[0],self.timebase[-1])
        
        for n in range(0,self.N):
            self.c[n].setData(self.timebase, self.x[n])
        self.plot.replot()

app = QtGui.QApplication(sys.argv)
frame = MainWindow()
frame.show()
sys.exit(app.exec_())

