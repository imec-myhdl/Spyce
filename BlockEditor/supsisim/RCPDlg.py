#!/usr/bin/python
# aim for python 2/3 compatibility
from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

from  Qt import QtWidgets, QtCore # see https://github.com/mottosso/Qt.py

from supsisim.const import respath

class BlkDlg(QtWidgets.QDialog):
    def __init__(self, line):
        super(BlkDlg, self).__init__(None)
        grid = QtWidgets.QGridLayout()
        self.line = line
        self.blkID = ''
        self.labels, self.params = self.parseParams(line)
        N = len(self.labels)
        self.Values = []
        for n in range(0,N):
            Lab = QtWidgets.QLabel(self.labels[n])
            Val = QtWidgets.QLineEdit(self.params[n].__str__())
            self.Values.append(Val)
            grid.addWidget(Lab,n,0)
            grid.addWidget(Val,n,1)
        
        self.pbOK = QtWidgets.QPushButton('OK')
        self.pbCANCEL = QtWidgets.QPushButton('CANCEL')
        grid.addWidget(self.pbOK,N,0)
        grid.addWidget(self.pbCANCEL,N,1)
        self.pbOK.clicked.connect(self.accept)
        self.pbCANCEL.clicked.connect(self.reject)
        self.setLayout(grid)

    def parseParams(self, line):
        lab = []
        val = []
        self.blkID = line['name']
        for name in line.keys():
            if name != 'name':
                lab.append(name.__str__())
                par = line[name].__str__()
                par = par.lstrip(' ')
                val.append(par)
        return lab,val

    def accept(self):
        N = len(self.labels)
        self.line = self.blkID
        for n in range(0,N):
            self.line += '|' + self.labels[n] +': ' + str(self.Values[n].text())
        super(BlkDlg, self).accept()

class ListDlg(QtWidgets.QDialog):
    def __init__(self, list, parent=None):
        super(ListDlg, self).__init__(parent)
        layout = QtWidgets.QGridLayout()
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.resize(380, 180)
        self.listWdg = QtWidgets.QListWidget()
        for item in list:
            self.listWdg.addItem(item)
        layout.addWidget(self.listWdg,0,0)
        self.pbOK = QtWidgets.QPushButton('OK')
        self.pbCANCEL = QtWidgets.QPushButton('CANCEL')
        layout.addWidget(self.pbOK,0,1)
        layout.addWidget(self.pbCANCEL,1,1)
        self.pbOK.clicked.connect(self.accept)
        self.pbCANCEL.clicked.connect(self.reject)
        # Check dialog.listWdg.currentRow _> index started from 0
        self.setLayout(layout)

def parsDialog(pars):
    #app = app = QApplication(sys.argv)
    dialog = BlkDlg(pars)
    res = dialog.exec_()
    return dialog.line

def INT031Dlg(nin, nout, pars):
    f = open(respath+'dialg/CardsID.txt','r')
    list = []
    for line in f:
        list.append(line)
    f.close()
    dlg = ListDlg(list)
    res = dlg.exec_()
    if res == 1:
        ln = pars.split('|')
        ln[1] = 'Card ID: ' + str(dlg.listWdg.currentRow()+1)
        pars = ln[0]
        for n in range(1,4):
            pars += '|' + ln[n]
    pars = parsDialog(pars)
    return pars

