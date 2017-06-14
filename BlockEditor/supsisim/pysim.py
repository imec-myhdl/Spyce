import sys
import os

import sip
#try:
#    sip.setapi('QString', 1)
#except ValueError: 
#    sip.setapi('QString', 2)

from pyqt45  import QApplication, QtCore
    

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
        app = QApplication(sys.argv)
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
