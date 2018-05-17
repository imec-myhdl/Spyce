#!/usr/bin/python
# aim for python 2/3 compatibility
from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

from  Qt import QtGui, QtWidgets, QtCore # see https://github.com/mottosso/Qt.py

import sys
import os

#try:
#    sip.setapi('QString', 1)
#except ValueError: 
#    sip.setapi('QString', 2)


import threading

from supsisim.pyEdit import SupsiSimMainWindow
from supsisim.library import Library

class supsisimul(threading.Thread):
    def __init__(self, filename = 'untitled', runflag = False):
        threading.Thread.__init__(self)
        if filename!='untitled':
            self.fname = QtCore.QFileInfo(filename)
            self.mypath = str(self.fname.absolutePath())
            self.fname = str(self.fname.baseName())
        else:
            self.fname = 'untitled'
            self.mypath =  os.getcwd()
        self.runflag = runflag

    def run(self):
        app = QtWidgets.QApplication(sys.argv)
        library = Library()
        library.setGeometry(20, 20, 400, 500)
        library.show()
        main = SupsiSimMainWindow(library, self.fname, self.mypath, self.runflag)
        main.setGeometry(500,100,1024,768)

        main.show()
        ret = app.exec_()
        app.deleteLater()

def supsim(fn = 'untitled'):
    th = supsisimul(fn)
    th.start()
