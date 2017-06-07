import sys
if sys.version_info>(3,0):
    import sip
    sip.setapi('QString', 1)
from PyQt4 import QtGui, QtCore
from supsisim.const import respath

class BlkDlg(QtGui.QDialog):
    def __init__(self, line):
        super(BlkDlg, self).__init__(None)
        grid = QtGui.QGridLayout()
        self.line = line
        self.blkID = ''
        self.labels, self.params = self.parseParams(line)
        N = len(self.labels)
        self.Values = []
        for n in range(0,N):
            Lab = QtGui.QLabel(self.labels[n])
            Val = QtGui.QLineEdit(self.params[n].__str__())
            self.Values.append(Val)
            grid.addWidget(Lab,n,0)
            grid.addWidget(Val,n,1)
        
        self.pbOK = QtGui.QPushButton('OK')
        self.pbCANCEL = QtGui.QPushButton('CANCEL')
        grid.addWidget(self.pbOK,N,0)
        grid.addWidget(self.pbCANCEL,N,1)
        self.pbOK.clicked.connect(self.accept)
        self.pbCANCEL.clicked.connect(self.reject)
        self.setLayout(grid)

    def parseParams(self, line):
        ln = line.split('|')
        N = len(ln)
        lab = []
        val = []
        self.blkID = ln[0]
        for n in range(1,N):
            ll = ln[n].split(':')
            lab.append(ll[0].__str__())
            par = ll[1].__str__()
            par = par.lstrip(' ')
            val.append(par)
        return lab,val

    def accept(self):
        N = len(self.labels)
        self.line = self.blkID
        for n in range(0,N):
            self.line += '|' + self.labels[n] +': ' + str(self.Values[n].text())
        super(BlkDlg, self).accept()

class ListDlg(QtGui.QDialog):
    def __init__(self, list, parent=None):
        super(ListDlg, self).__init__(parent)
        layout = QtGui.QGridLayout()
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.resize(380, 180)
        self.listWdg = QtGui.QListWidget()
        for item in list:
            self.listWdg.addItem(item)
        layout.addWidget(self.listWdg,0,0)
        self.pbOK = QtGui.QPushButton('OK')
        self.pbCANCEL = QtGui.QPushButton('CANCEL')
        layout.addWidget(self.pbOK,0,1)
        layout.addWidget(self.pbCANCEL,1,1)
        self.pbOK.clicked.connect(self.accept)
        self.pbCANCEL.clicked.connect(self.reject)
        # Check dialog.listWdg.currentRow _> index started from 0
        self.setLayout(layout)

def parsDialog(pars):
    #app = app = QtGui.QApplication(sys.argv)
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
        pass
    pars = parsDialog(pars)
    return pars

