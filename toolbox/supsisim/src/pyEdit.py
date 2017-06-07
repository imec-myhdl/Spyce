#!/usr/bin/python

import sys
import os
if sys.version_info>(3,0):
    import sip
    sip.setapi('QString', 1)
from PyQt4 import QtGui, QtCore

from supsisim.block import Block
from supsisim.node import Node
from supsisim.connection import Connection
from supsisim.editor import Editor
from supsisim.library import Library
from supsisim.scene import Scene, GraphicsView
from supsisim.dialg import IO_Dialog
from supsisim.const import respath, pycmd

DEBUG = False

class SupsiSimMainWindow(QtGui.QMainWindow):
    def __init__(self, library, fname, mypath, runflag, parent=None):
        super(SupsiSimMainWindow, self).__init__(parent)
        self.resize(1024, 768)
        self.centralWidget = QtGui.QWidget(self)
        self.verticalLayout = QtGui.QVBoxLayout(self.centralWidget)
        self.verticalLayout.setMargin(0)
        self.view = GraphicsView(self.centralWidget)
        self.view.setMouseTracking(True)
        self.scene = Scene(self)
        self.view.setScene(self.scene)
        self.view.setRenderHint(QtGui.QPainter.Antialiasing)
        self.verticalLayout.addWidget(self.view)
        self.setCentralWidget(self.centralWidget)
        self.addactions()
        self.addMenubar()
        self.addToolbars()
        self.filename = fname
        self.path = mypath
        self.library = library
        self.runflag = runflag
        if fname != 'untitled':
            self.scene.loadDgm(self.getFullFileName())
            
        self.setWindowTitle(self.filename)
        self.status = self.statusBar()
        self.evpos = QtCore.QPointF(0,0)
        self.editor = Editor(self)
        self.editor.install(self.scene)
        self.status.showMessage('Ready')

    def addactions(self):
        mypath = respath + '/icons/'

        self.newFileAction = QtGui.QAction(QtGui.QIcon(mypath+'filenew.png'),
                                                '&Open', self,
                                                shortcut = 'Ctrl+N',
                                                statusTip = 'New File',
                                                triggered = self.newFile)
        
        self.openFileAction = QtGui.QAction(QtGui.QIcon(mypath+'fileopen.png'),
                                                '&Open', self,
                                                shortcut = 'Ctrl+O',
                                                statusTip = 'Open File',
                                                triggered = self.openFile)

        self.saveFileAction = QtGui.QAction(QtGui.QIcon(mypath+'filesave.png'),
                                                '&Save', self,
                                                shortcut = 'Ctrl+S',
                                                statusTip = 'Save File',
                                                triggered = self.saveFile)

        self.copyAction = QtGui.QAction(QtGui.QIcon(mypath+'copy.png'),
                                            '&Copy', self,
                                            shortcut = 'Ctrl+C',
                                            statusTip = 'Copy',
                                            triggered = self.copyAct)

        self.pasteAction = QtGui.QAction(QtGui.QIcon(mypath+'paste.png'),
                                             '&Paste', self,
                                             shortcut = 'Ctrl+V',
                                             statusTip = 'Paste',
                                             triggered = self.pasteAct)

        self.printAction = QtGui.QAction(QtGui.QIcon(mypath+'print.png'),
                                             '&Print', self,
                                             shortcut = 'Ctrl+P',
                                             statusTip = 'Print schematic',
                                             triggered = self.print_scheme)

        self.exitAction = QtGui.QAction(QtGui.QIcon(mypath+'exit.png'),
                                            '&Exit',self,
                                            shortcut = 'Ctrl+X',
                                            statusTip = 'Exit Application',
                                            triggered = self.close)
                                            
        self.startPythonAction = QtGui.QAction(QtGui.QIcon(mypath+'python.png'),
                                               'Start iPython',self,
                                               statusTip = 'Start iPython',
                                               triggered = self.startpythonAct)

        self.runAction = QtGui.QAction(QtGui.QIcon(mypath+'run.png'),
                                           'Simulate',self,
                                           statusTip = 'Simulate',
                                           triggered = self.runAct)

        self.codegenAction = QtGui.QAction(QtGui.QIcon(mypath+'codegen.png'),
                                               'Generate C-code',self,
                                               statusTip = 'Generate C-Code',
                                               triggered = self.codegenAct)

        self.setCodegenAction = QtGui.QAction(QtGui.QIcon(mypath+'settings.png'),
                                                'Block settings',self,
                                                statusTip = 'Block settings',
                                                triggered = self.setcodegenAct)

        self.debugAction = QtGui.QAction(QtGui.QIcon(mypath+'debug.png'),
                                             'Debugging',self,
                                             statusTip = 'Debug infos',
                                             triggered = self.debugAct)                                           
    def addToolbars(self):
        toolbarF = self.addToolBar('File')
        toolbarF.addAction(self.newFileAction)
        toolbarF.addAction(self.openFileAction)
        toolbarF.addAction(self.saveFileAction)
        toolbarF.addAction(self.printAction)
        toolbarF.addAction(self.exitAction)

        toolbarE = self.addToolBar('Edit')
        toolbarE.addAction(self.copyAction)
        toolbarE.addAction(self.pasteAction)

        toolbarS = self.addToolBar('Simuation')
        toolbarS.addAction(self.runAction)
        toolbarS.addAction(self.codegenAction)
        toolbarS.addAction(self.setCodegenAction)

        toolbarP = self.addToolBar('Python')
        toolbarP.addAction(self.startPythonAction)
        if DEBUG:
            toolbarD = self.addToolBar('Debug')
            toolbarD.addAction(self.debugAction)

    def addMenubar(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.openFileAction)
        fileMenu.addAction(self.saveFileAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAction)
        
        editMenu = menubar.addMenu('&Edit')
        editMenu.addAction(self.copyAction)
        editMenu.addAction(self.pasteAction)
#        editMenu.addSeparator()
#        editMenu.addAction(self.updateAction)

        simMenu = menubar.addMenu('&Simulation')
        simMenu.addAction(self.runAction)
        simMenu.addAction(self.codegenAction)

        setMenu = menubar.addMenu('Se&ttings')
        setMenu.addAction(self.setCodegenAction)

    def copyAct(self):
        self.scene.selection = []
        p = self.scene.selectionArea()
        self.scene.selection = self.scene.items(p)
        if self.scene.selection == []:
            self.scene.selection = self.scene.selectedItems()

    def pasteAct(self):
        if self.scene.selection != []:
            for item in self.scene.selection:
                if isinstance(item, Block) or isinstance(item, Node):
                    try:
                        item.clone(QtCore.QPointF(200,200))
                    except:
                        pass
            for item in self.scene.selection:
                if isinstance(item, Connection):
                    try:
                        c = item.clone(QtCore.QPointF(200,200))
                        c.update_ports_from_pos()
                    except:
                        pass        

    def updateAct(self):
        items = self.scene.items()
        for item in items:
            if isinstance(item, Connection):
                self.scene.removeItem(item)
                item.update_path()
            
    
    def getFullFileName(self):
        return(self.path + '/' + self.filename + '.dgm')

    def askSaving(self):
        items = self.scene.items()
        if len(items) == 0:
            return QtGui.QMessageBox.Discard
        
        msg = QtGui.QMessageBox('The Document has been modified',
                                    'Do you want to save your changes?',
                                    QtGui.QMessageBox.Question,
                                    QtGui.QMessageBox.Save,
                                    QtGui.QMessageBox.Discard,
                                    QtGui.QMessageBox.Cancel)
        ret = msg.exec_()
        return ret
            
    def newFile(self):
        fname = self.filename
        try:
            os.remove(fname+'.py')
        except:
            pass
        ret = self.askSaving()
        if ret == QtGui.QMessageBox.Save:
            self.saveFile()
        elif ret != QtGui.QMessageBox.Cancel:
            self.scene.newDgm()
            self.filename = 'untitled'
            self.path = os.getcwd()
            self.setWindowTitle(self.filename)
        
    def openFile(self):
        fname = self.filename
        try:
            os.remove(fname+'.py')
        except:
            pass
        ret = self.askSaving()
        if ret == QtGui.QMessageBox.Save:
            self.saveFile()
            self.filename = 'untitled'
            self.path = os.getcwd()
            self.setWindowTitle(self.filename)
        elif ret != QtGui.QMessageBox.Cancel:
            self.scene.newDgm()
            filename = QtGui.QFileDialog.getOpenFileName(self, 'Open', '.', filter='*.dgm')
            if filename != '':
                fname = QtCore.QFileInfo(filename)
                self.filename = str(fname.baseName())
                self.path = str(fname.absolutePath())
                self.setWindowTitle(self.filename)
                self.scene.loadDgm(self.getFullFileName())
        
    def saveFile(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save', self.path+'/'+self.filename, filter='*.dgm')
        if filename != '':
            fname = QtCore.QFileInfo(filename)
            self.filename = str(fname.baseName())
            self.path = str(fname.absolutePath())
            self.setWindowTitle(self.filename)
            self.scene.saveDgm(self.getFullFileName())

    def print_scheme(self):
        self.printer = QtGui.QPrinter()
        printDialog = QtGui.QPrintDialog(self.printer)
        if (printDialog.exec_() == QtGui.QDialog.Accepted):
            painter = QtGui.QPainter(self.printer)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.setRenderHint(QtGui.QPainter.TextAntialiasing)
            self.scene.clearSelection()
            self.scene.render(painter)

    def parBlock(self):
        item = self.scene.item
        dialog = IO_Dialog(self)
        dialog.spbInput.setValue(item.inp)
        dialog.spbOutput.setValue(item.outp)
        if item.inp == 0 or item.iosetble==False:
            dialog.spbInput.setEnabled(False)
        if item.outp == 0 or item.iosetble==False:
            dialog.spbOutput.setEnabled(False)
            
        name = item.name
        flip = item.flip
        icon = item.icon
        params = item.params
        iosetble = item.iosetble
        res = dialog.exec_()
        if res == 1 and iosetble:
            item.remove()
            inp = dialog.spbInput.value()
            outp = dialog.spbOutput.value()
            b = Block(None, self.scene, name, inp, outp, iosetble, icon, params, flip)
            b.setPos(self.scene.evpos)

    def startpythonAct(self):
        os.system(pycmd)

    def debugAct(self):
        self.scene.debugInfo()

    def runAct(self):
        self.scene.simrun()

    def codegenAct(self):
        self.scene.codegen(True)

    def setrunAct(self):
        self.scene.runDlg()

    def setcodegenAct(self):
        self.scene.codegenDlg()

    def closeEvent(self,event):
        try:
            os.remove('tmp.py')
        except:
            pass
        ret = self.askSaving()
        if ret == QtGui.QMessageBox.Save:
            self.saveFile()
            library.closeFlag = True
            library.close()
            event.accept()
        elif ret == QtGui.QMessageBox.Discard:

            self.library.closeFlag = True
            self.library.close()
            event.accept()
        else:
            event.ignore()
                
