#!/usr/bin/python

import sys
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from os import system
from scipy import loadtxt, shape

import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

class MainWindow(QMainWindow):
    def __init__(self,fname, tEnd):
        QMainWindow.__init__(self)
        self.resize(600,400)
        self.setWindowTitle('Simulation')
        self.fname = fname
        self.tEnd = tEnd
        self.setGui()
        self.Run()

    def setGui(self):
        self.main_frame = QWidget()
        
        plot_frame = QWidget()
        
        self.dpi = 100
        self.fig = Figure((6.0, 4.0), dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        
        self.axes = self.fig.add_subplot(111)
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)

        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)

    def Run(self):
        self.axes.clear()
        self.axes.grid(True)
        if self.tEnd == 0:
            tf = ''
        else:
            tf = str(self.tEnd)
        cmd = './' + self.fname + ' -f' + tf + ' > x.x'
        system(cmd)
        x = loadtxt('x.x')
        N=shape(x)[1]
        if shape(x)[0] != 0:
            self.axes.plot(x[:,0],x[:,1:N])
            self.canvas.draw()
        system('rm x.x')
                
app = QApplication(sys.argv)
if len(sys.argv) > 1:
    fname = str(sys.argv[1])
    if len(sys.argv) == 3:
        tEnd = float(sys.argv[2])
    else:
        tEnd = 10.0

    main = MainWindow(fname,tEnd)
    main.show()
    sys.exit(app.exec_())
else:
    print('Not enough argument! pySim fname [tEnd]')
    sys.exit(1)


    
        
