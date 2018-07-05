#!/usr/bin/python
# aim for python 2/3 compatibility
from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

from  Qt import QtGui, QtWidgets, QtCore # see https://github.com/mottosso/Qt.py
from  Qt.QtPrintSupport import QPrinter, QPrintDialog

import os
#if sys.version_info>(3,0):
#    import sip
#    sip.setapi('QString', 1)


from supsisim.block import Block
from supsisim.node import Node
from supsisim.connection import Connection
from supsisim.editor import Editor
from supsisim.library import Library
from supsisim.scene import Scene, GraphicsView
from supsisim.dialg import IO_Dialog, convertSymDialog
from supsisim.const import respath, pycmd
from supsisim.port import Port,InPort,OutPort,InNodePort,OutNodePort
import libraries

DEBUG = False

class SupsiSimMainWindow(QtWidgets.QMainWindow):
    def __init__(self, library, fname, mypath, runflag, parent=None):
        super(SupsiSimMainWindow, self).__init__(parent)
        self.resize(1024, 768)
        
#        self.centralWidget = QtWidgets.QTabWidget()
#        self.view = GraphicsView(self.centralWidget)
#        self.view.setMouseTracking(True)
#        self.scene = Scene(self)
#        self.view.setScene(self.scene)
#        self.view.setRenderHint(QtGui.QPainter.Antialiasing)
#        self.centralWidget.addTab(self.view,fname)
#        self.setCentralWidget(self.centralWidget)
        
        self.centralWidget = QtWidgets.QWidget(self)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralWidget)
        self.verticalLayout.setContentsMargins(0,0,0,0)
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

        self.newFileAction = QtWidgets.QAction(QtGui.QIcon(mypath+'filenew.png'),
                                                '&New', self,
                                                shortcut = 'Ctrl+N',
                                                statusTip = 'New File',
                                                triggered = self.newFile)
        
        self.openFileAction = QtWidgets.QAction(QtGui.QIcon(mypath+'fileopen.png'),
                                                '&Open', self,
                                                shortcut = 'Ctrl+O',
                                                statusTip = 'Open File',
                                                triggered = self.openFile)

        self.saveFileAction = QtWidgets.QAction(QtGui.QIcon(mypath+'filesave.png'),
                                                '&Save', self,
                                                shortcut = 'Ctrl+S',
                                                statusTip = 'Save File',
                                                triggered = self.saveFile)

        self.copyAction = QtWidgets.QAction(QtGui.QIcon(mypath+'copy.png'),
                                            '&Copy', self,
                                            shortcut = 'Ctrl+C',
                                            statusTip = 'Copy',
                                            triggered = self.copyAct)

        self.pasteAction = QtWidgets.QAction(QtGui.QIcon(mypath+'paste.png'),
                                             '&Paste', self,
                                             shortcut = 'Ctrl+V',
                                             statusTip = 'Paste',
                                             triggered = self.pasteAct)
        
        self.convertSymbolAction = QtWidgets.QAction(QtGui.QIcon(mypath+'paste.png'),
                                             '&Convert symbol', self,
                                             statusTip = 'Convert symbol',
                                             triggered = self.convertSymAct)

        self.printAction = QtWidgets.QAction(QtGui.QIcon(mypath+'print.png'),
                                             '&Print', self,
                                             shortcut = 'Ctrl+P',
                                             statusTip = 'Print schematic',
                                             triggered = self.print_scheme)

        self.exitAction = QtWidgets.QAction(QtGui.QIcon(mypath+'exit.png'),
                                            '&Exit',self,
                                            shortcut = 'Ctrl+X',
                                            statusTip = 'Exit Application',
                                            triggered = self.close)
                                            
        self.startPythonAction = QtWidgets.QAction(QtGui.QIcon(mypath+'python.png'),
                                               'Start iPython',self,
                                               statusTip = 'Start iPython',
                                               triggered = self.startpythonAct)

        self.runAction = QtWidgets.QAction(QtGui.QIcon(mypath+'run.png'),
                                           'Simulate',self,
                                           statusTip = 'Simulate',
                                           triggered = self.runAct)

        self.codegenAction = QtWidgets.QAction(QtGui.QIcon(mypath+'codegen.png'),
                                               'Generate C-code',self,
                                               statusTip = 'Generate C-Code',
                                               triggered = self.codegenAct)

        self.setCodegenAction = QtWidgets.QAction(QtGui.QIcon(mypath+'settings.png'),
                                                'Block settings',self,
                                                statusTip = 'Block settings',
                                                triggered = self.setcodegenAct)

        self.debugAction = QtWidgets.QAction(QtGui.QIcon(mypath+'debug.png'),
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
        editMenu.addAction(self.convertSymbolAction)
#        editMenu.addSeparator()
#        editMenu.addAction(self.updateAction)

        simMenu = menubar.addMenu('&Simulation')
        simMenu.addAction(self.runAction)
        simMenu.addAction(self.codegenAction)

        setMenu = menubar.addMenu('Se&ttings')
        setMenu.addAction(self.setCodegenAction)
        
    def descend(self,item):
        pass
    
    def ascend(self):
        pass        
        
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
                    ports = []
                    for portItem in self.scene.selection:
                        if isinstance(portItem, Node):
                            ports.append(portItem.port_out)
                            ports.append(portItem.port_in)
                    if (item.port1 in self.scene.selection or item.port1 in ports) and (item.port2 in ports or item.port2 in self.scene.selection):
                        try:
                            c = item.clone(QtCore.QPointF(200,200))
                            c.update_ports_from_pos()
                        except:
                            pass        
    
    def convertSymAct(self):
        items = []
        inp = 0
        outp = 0
        for item in self.scene.items(self.scene.selectionArea()):
            if isinstance(item,Block) or isinstance(item,Connection) or isinstance(item,Node):
                items.append(item.toPython())
            if isinstance(item,Node):
                if not item.port_in.connections:
                    inp += 1
                if not item.port_out.connections:
                    outp += 1
            if isinstance(item,Block):
                for port in item.ports():
                    if not port.connections:
                        if isinstance(port,InPort):
                            inp += 1
                        elif isinstance(port,OutPort):
                            outp += 1
        dialog = convertSymDialog()
        ret = dialog.getRet()
        if ret:
            for item in self.scene.selectedItems():    
                try:
                    item.remove()
                except:
                    pass
            name = ret['name']
            icon = ret['icon']
            libname = 'library_symbols'
            
            attributes = {'name':name,'input':inp,'output':outp,'icon':icon,'libname':libname,'type':'symbol'} 
                    
            
            parameters = ret['parameters']
            properties = ret['properties']
            views = []
            
            data = 'attributes = ' + str(attributes) + '\nproperties = ' + str(properties) + '\nparameters = ' + str(parameters) + '\nviews = ' + str(views) + '\nitems = ' + str(items)
            

            self.path = os.getcwd()            
            f = open(self.path + '/libraries/library_symbols/block_' + name + '.py','w+')
            f.write(str(data))
            f.close()
            
            libraries.getBlock(name,'symbols',None,self.scene)      
            
            if self.library.type == 'symbolView':
                self.library.symbolView()
                self.library.tabs.setCurrentWidget(self.library.symbolTab)
            else:
                self.library.listView()
                self.library.libraries.setCurrentItem(self.library.libraries.findItems('symbols',QtCore.Qt.MatchExactly)[0])
            
            
    
    def updateAct(self):
        items = self.scene.items()
        for item in items:
            if isinstance(item, Connection):
                self.scene.removeItem(item)
                item.update_path()
            
    
    def getFullFileName(self):
        return(self.path + '/' + self.filename + '.py')

    def askSaving(self):
        items = self.scene.items()
        if len(items) == 0:
            return QtWidgets.QMessageBox.Discard
        
        msg = QtWidgets.QMessageBox()
        msg.setText('The Document has been modified')
        msg.setInformativeText('Do you want to save your changes?')
        msg.setStandardButtons(     QtWidgets.QMessageBox.Question |
                                    QtWidgets.QMessageBox.Save |
                                    QtWidgets.QMessageBox.Discard |
                                    QtWidgets.QMessageBox.Cancel)
        ret = msg.exec_()
        return ret
            
    def newFile(self):
        fname = self.filename
#        try:
#            os.remove(fname+'.py')
#        except:
#            pass
        ret = self.askSaving()
        cancel = False
        if ret == QtWidgets.QMessageBox.Save:
            cancel = self.saveFile()
        if ret != QtWidgets.QMessageBox.Cancel and not cancel:
            self.scene.newDgm()
            self.filename = 'untitled'
            self.path = os.getcwd()
            self.setWindowTitle(self.filename)
        
    def openFile(self):
        fname = self.filename
#        try:
#            os.remove(fname+'.py')
#        except:
#            pass
        
#            self.filename = 'untitled'
#            self.path = os.getcwd()
#            self.setWindowTitle(self.filename)
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open', self.path+'/saves/', filter='*.py')
        if isinstance(filename, tuple):
            filename = filename[0]
        if filename != '':
            ret = self.askSaving()
            if ret == QtWidgets.QMessageBox.Save:
                self.saveFile()
            if ret != QtWidgets.QMessageBox.Cancel:
                self.scene.newDgm()
                fname = QtCore.QFileInfo(filename)
                self.filename = str(fname.baseName())
                self.path = str(fname.absolutePath())
                self.setWindowTitle(self.filename)
                self.scene.loadPython(self.filename,self.path)
        
    def saveFile(self):
        filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save', self.path+'/saves/'+self.filename, filter='*.py')
        if isinstance(filename, tuple):
                filename = filename[0]
        if filename != '':
            fname = QtCore.QFileInfo(filename)
            self.filename = str(fname.baseName())
            self.path = str(fname.absolutePath())
            self.setWindowTitle(self.filename)
            self.scene.savePython(self.getFullFileName())
        else:
            return True

    def print_scheme(self):
        self.printer = QPrinter()
        printDialog = QPrintDialog(self.printer)
        if (printDialog.exec_() == QtWidgets.QDialog.Accepted):
            painter = QtGui.QPainter(self.printer)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.setRenderHint(QtGui.QPainter.TextAntialiasing)
            self.scene.clearSelection()
            self.scene.render(painter)

    def parBlock(self):
        item = self.scene.item
        dialog = IO_Dialog(self)
        dialog.spbInput.setValue(item.inp if isinstance(item.inp, int) else len(item.inp))
        dialog.spbOutput.setValue(item.outp if isinstance(item.outp, int) else len(item.outp))
        
        if item.inp == 0 or not item.parameters or not 'inp' in item.parameters:
            dialog.spbInput.setEnabled(False)
        else:
            dialog.spbInput.setMinimum(1)
        if item.outp == 0 or not item.parameters or not 'outp' in item.parameters:
            print(not item.parameters)
            dialog.spbOutput.setEnabled(False)
        else:
            dialog.spbOutput.setMinimum(1)
            


        res = dialog.exec_()
        if res == 1:
            item.remove()
            
            name = item.name
            flip = item.flip
            icon = item.icon
            libname = item.libname
            inp = dialog.spbInput.value()
            outp = dialog.spbOutput.value()
            
            attributes = {'name':name,'input':inp,'output':outp,'icon':icon,'flip':flip,'libname':libname}            
            parameters = item.parameters
            properties = item.properties
            views = item.views
            
            b = Block(attributes,parameters,properties,views,None, self.scene)
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
        if ret == QtWidgets.QMessageBox.Save:
            self.saveFile()
            Library.closeFlag = True
            Library.close()
            event.accept()
        elif ret == QtWidgets.QMessageBox.Discard:

            self.library.closeFlag = True
            self.library.close()
            event.accept()
        else:
            event.ignore()
                
