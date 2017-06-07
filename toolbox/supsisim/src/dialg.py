import sys
if sys.version_info>(3,0):
    import sip
    sip.setapi('QString', 1)
from PyQt4 import QtGui, QtCore

from supsisim.const import path

class IO_Dialog(QtGui.QDialog):
    def __init__(self,parent=None):
        super(IO_Dialog, self).__init__(parent)
        layout = QtGui.QGridLayout()
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.resize(380, 180)
        self.spbInput = QtGui.QSpinBox()
        self.spbOutput = QtGui.QSpinBox()
        self.spbInput.setValue(1)
        self.spbOutput.setValue(1)

        label2 = QtGui.QLabel('Number of inputs:')
        label3 = QtGui.QLabel('Number of outputs')
        self.pbOK = QtGui.QPushButton('OK')
        self.pbCANCEL = QtGui.QPushButton('CANCEL')
        layout.addWidget(self.spbInput,0,1)
        layout.addWidget(self.spbOutput,1,1)
        layout.addWidget(label2,0,0)
        layout.addWidget(label3,1,0)
        layout.addWidget(self.pbOK,2,0)
        layout.addWidget(self.pbCANCEL,2,1)
        self.setLayout(layout)
        self.pbOK.clicked.connect(self.accept)
        self.pbCANCEL.clicked.connect(self.reject)
        
class BlockName_Dialog(QtGui.QDialog):
    def __init__(self,parent=None):
        super(BlockName_Dialog, self).__init__(parent)
        layout = QtGui.QGridLayout()
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.resize(380, 100)
        self.name = QtGui.QLineEdit()

        label1 = QtGui.QLabel('Block ID:')
        self.pbOK = QtGui.QPushButton('OK')
        self.pbCANCEL = QtGui.QPushButton('CANCEL')
        layout.addWidget(label1,0,0)
        layout.addWidget(self.name,0,1)
        layout.addWidget(self.pbOK,2,0)
        layout.addWidget(self.pbCANCEL,2,1)
        self.setLayout(layout)
        self.pbOK.clicked.connect(self.accept)
        self.pbCANCEL.clicked.connect(self.reject)

class RTgenDlg(QtGui.QDialog):
    def __init__(self, parent=None):
        super(RTgenDlg, self).__init__(None)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.resize(380, 100)
        lab1 = QtGui.QLabel('Template Makefile')
        self.template = QtGui.QLineEdit('')
        btn_template = QtGui.QPushButton('BROWSE...')
        lab2 = QtGui.QLabel('Additional Objs')
        self.addObjs = QtGui.QLineEdit('')
        btn_addObjs = QtGui.QPushButton('BROWSE...')
        lab3 = QtGui.QLabel('Sampling Time')
        self.Ts = QtGui.QLineEdit('')
        lab4 = QtGui.QLabel('Parameter script')
        self.parscript = QtGui.QLineEdit('')
        btn_script = QtGui.QPushButton('BROWSE...')
        lab5 = QtGui.QLabel('Final Time')
        self.Tf = QtGui.QLineEdit('')
        pbOK = QtGui.QPushButton('OK')
        pbCANCEL = QtGui.QPushButton('CANCEL')
        grid = QtGui.QGridLayout()
        grid.addWidget(lab1,0,0)
        grid.addWidget(self.template,0,1)
        grid.addWidget(btn_template,0,2)
        grid.addWidget(lab2,1,0)
        grid.addWidget(self.addObjs,1,1)
        grid.addWidget(btn_addObjs,1,2)
        grid.addWidget(lab3,2,0)
        grid.addWidget(self.Ts,2,1)
        grid.addWidget(lab4,3,0)
        grid.addWidget(self.parscript,3,1)
        grid.addWidget(btn_script,3,2)
        grid.addWidget(lab5,4,0)
        grid.addWidget(self.Tf,4,1)
        grid.addWidget(pbOK,6,0)
        grid.addWidget(pbCANCEL,6,1)
        pbOK.clicked.connect(self.accept)
        pbCANCEL.clicked.connect(self.reject)
        btn_template.clicked.connect(self.getTemplate)
        btn_addObjs.clicked.connect(self.getObjs)
        btn_script.clicked.connect(self.getScript)
        self.setLayout(grid)

    def getTemplate(self):
        fname = QtGui.QFileDialog.getOpenFileName(self,'Open Template Makefile',
                                                  path+'CodeGen/templates', 'Template (*.tmf)')
        if len(fname) != 0:
            ln = fname.split('/')
            templ = ln[-1].__str__()
            self.template.setText(templ)

    def getObjs(self):
        fname = QtGui.QFileDialog.getOpenFileName(self,'Additional libraries',
                                                  '.','Dynamic libraries (*.so)')
        if len(fname) != 0:
            ln = fname.split('/')
            libname = ln[-1].__str__()
            self.addObjs.setText(libname)

    def getScript(self):
        fname = QtGui.QFileDialog.getOpenFileName(self,'Open Python script',
                                                  '.', 'Python file (*.py)')
        if len(fname) != 0:
            ln = fname.split('/')
            script = ln[-1].__str__()
            self.parscript.setText(script)

