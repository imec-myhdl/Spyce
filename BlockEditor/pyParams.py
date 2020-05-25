
# aim for python 2/3 compatibility
from builtins import str
from builtins import range
from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

from  Qt import QtWidgets # see https://github.com/mottosso/Qt.py

import sys

# import userinterface generated from SendPars.ui
from SendPars import Ui_Dialog
    
import supsictrl.unixsocket as sk

#import socket
import struct
import time

#import numpy as np


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        # Set up the user interface from Designer.
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.update()
        self.connect_widget()
        self.add_widgets()

        self.sock = sk.open_client('/tmp/ssock')

    def add_widgets(self):
        for i in reversed(list(range(self.ui.gridLayout.count()))): 
            self.ui.gridLayout.itemAt(i).widget().setParent(None)           

        self.ui.gridLayout.setRowStretch(12,1)
        self.ui.gridLayout.setVerticalSpacing(5)
        N = self.ui.spVars.value()
        for n in range(N):
            lab = QtWidgets.QLabel('Parameter ' + str(n+1) + ': ')
            self.ui.gridLayout.addWidget(lab,n,0);
            ed = QtWidgets.QLineEdit('0.0')            
            self.ui.gridLayout.addWidget(ed,n,1);
        
    def connect_widget(self):
        self.ui.pbSend.clicked.connect(self.pbSendClicked)
        self.ui.spVars.valueChanged.connect(self.add_widgets)

    def pbSendClicked(self):
        N = self.ui.spVars.value()
        strdata='i ' + str(N)+'d'
        val = []
        for n in range(N):
            val.append(float(self.ui.gridLayout.itemAtPosition(n,1).widget().text().__str__()))
        msg = struct.pack(strdata, 1, *val)
        self.sock.sendall(msg)

    def closeEvent(self, event):
        msg = struct.pack('i d', 0, 0.0)
        self.sock.sendall(msg)
        time.sleep(1)
        sk.close_client(self.sock, '/tmp/ssock')

app = QApplication(sys.argv)
frame = MainWindow()
frame.show()
sys.exit(app.exec_())

    
