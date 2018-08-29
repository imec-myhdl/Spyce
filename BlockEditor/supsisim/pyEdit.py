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
from supsisim.dialg import IO_Dialog, convertSymDialog, viewConfigDialog,error
from supsisim.const import respath, pycmd, PD,PW,BWmin
from supsisim.port import Port,InPort,OutPort,InNodePort,OutNodePort
import libraries

DEBUG = False

class SupsiSimMainWindow(QtWidgets.QMainWindow):
    def __init__(self, library, fname, mypath, runflag, parent=None):
        super(SupsiSimMainWindow, self).__init__(parent)
        self.resize(1024, 768)
        self.centralWidget = QtWidgets.QTabWidget()
        self.centralWidget.setTabsClosable(True)
        self.centralWidget.tabCloseRequested.connect(self.closeTab)
        self.centralWidget.currentChanged.connect(self.onChange)   
        self.setCentralWidget(self.centralWidget)
        
#        self.centralWidget = QtWidgets.QWidget(self)
#        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralWidget)
#        self.verticalLayout.setContentsMargins(0,0,0,0)
#        self.view = GraphicsView(self.centralWidget)
#        self.view.setMouseTracking(True)
#        self.scene = Scene(self)
#        self.view.setScene(self.scene)
#        self.view.setRenderHint(QtGui.QPainter.Antialiasing)
#        self.verticalLayout.addWidget(self.view)
#        self.setCentralWidget(self.centralWidget)
        
        
        
        self.addactions()
        self.addMenubar()
        self.addToolbars()
        self.filename = fname
        self.path = mypath
        self.library = library
        self.runflag = runflag
        if fname != 'untitled':
            self.scene.loadDgm(self.getFullFileName())
            
        self.setWindowTitle('Editor')
        self.status = self.statusBar()
        self.evpos = QtCore.QPointF(0,0)
        self.editor = Editor(self)     
        self.newFile()
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
                                             
        self.addNodeAction = QtWidgets.QAction(QtGui.QIcon(mypath+'AddNode.png'),
                                             '&Add Node', self,
                                             shortcut = 'N',
                                             statusTip = 'Add Node',
                                             triggered = self.addNodeAct)                                    
        
        self.convertSymbolAction = QtWidgets.QAction(QtGui.QIcon(mypath+'convertSymbol.png'),
                                             '&Convert symbol', self,
                                             statusTip = 'Convert symbol',
                                             triggered = self.convertSymAct)
                                             
        self.commentAction = QtWidgets.QAction(QtGui.QIcon(mypath+'comment.png'),
                                             '&Add Comment', self,
                                             shortcut = 'C',
                                             statusTip = 'Add Comment',
                                             triggered = self.addCommentAct)     

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
                                                
        self.viewConfigAction = QtWidgets.QAction(QtGui.QIcon(mypath+'viewConfig.png'),
                                                'View settings',self,
                                                statusTip = 'View settings',
                                                triggered = self.viewConfigAct)
                                                
                                                
        self.editConstants = QtWidgets.QAction(QtGui.QIcon(mypath+'viewConfig.png'),
                                                'Edit settings',self,
                                                statusTip = 'Edit settings',
                                                triggered = self.editSettingsAction)

        self.debugAction = QtWidgets.QAction(QtGui.QIcon(mypath+'debug.png'),
                                             'Debugging',self,
                                             statusTip = 'Debug infos',
                                             triggered = self.debugAct)     
                                             
        
        self.testIndex = QtWidgets.QAction(QtGui.QIcon(mypath+'debug.png'),
                                             '&Test index',self,
                                             statusTip = 'Test index',
                                             triggered = self.testIndexAct) 
        
                                             
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
        toolbarE.addAction(self.convertSymbolAction)
        toolbarE.addAction(self.addNodeAction)
        toolbarE.addAction(self.commentAction)

        toolbarS = self.addToolBar('Simuation')
        toolbarS.addAction(self.runAction)
        toolbarS.addAction(self.codegenAction)
        toolbarS.addAction(self.setCodegenAction)
        

        toolbarP = self.addToolBar('Python')
        toolbarP.addAction(self.startPythonAction)
        toolbarP.addAction(self.testIndex)
        if DEBUG:
            toolbarD = self.addToolBar('Debug')
            toolbarD.addAction(self.debugAction)
            
    def testIndexAct(self):
        print(self.centralWidget.currentIndex()) 
        #point = self.view.mapToScene(self.view.viewport().width()/2,self.view.viewport().height()/2)
        #print(point.x(),point.y())
            
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
        setMenu.addAction(self.viewConfigAction)
        setMenu.addAction(self.editConstants)
    
    def editSettingsAction(self):
        from supsisim.const import viewEditors
        os.system(viewEditors['python'] + ' supsisim/const.py')
    
    def viewConfigAct(self):
        dialog = viewConfigDialog()
        ret = dialog.getRet()
        if ret:
            path = os.getcwd()
            fname = '/supsisim/const.py'
            f = open(path + fname,'r')
            lines = f.readlines()
            f.close()
            
            for index,line in enumerate(lines):
                if line.startswith('viewEditors = '):
                    del lines[index:]
                    
            for index,view in enumerate(ret):
                if index == 0:
                    string = 'viewEditors = dict('
                else:
                    string = "                   "
                string += view['key'] + "='" + view['text'] + "'"
                if index == len(ret) - 1:
                    string += ')'
                else:
                    string += ',\n'
                lines.append(string)
            
            
            f = open(path + fname,'w+')
            f.write("".join(lines))
            f.close()
            
            
            
        
    
    def onChange(self,i):
        self.view=self.centralWidget.widget(i)
        self.scene=self.centralWidget.widget(i).scene()
        self.editor.install(self.scene)
#        for item in self.scene.items():
#            if isinstance(item,Block) and item.type == 'symbol':
#                item.reloadPorts()
#        self.scene.savePython('tmp.py')
#        self.scene.newDgm()
#        self.scene.loadPython('tmp',None,False)
#        try:
#            os.remove('tmp.py')
#        except:
#            pass
           
    def descend(self,item):
        self.view.returnSymbol = True
        self.newFile(item.name,symbol=True,blockname=item.blockname,libname=item.libname)
        self.scene.loadPython('libraries.library_' + item.libname + '.' + item.blockname + '_diagram',None)
    
    def ascend(self):
        pass        
    
    def addNodeAct(self):
        mimeData = QtCore.QMimeData()
            
        data = 'Node'
        mimeData.setText(data)
        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.exec_(QtCore.Qt.CopyAction)    
        
    def addCommentAct(self):
        mimeData = QtCore.QMimeData()
            
        data = 'Comment'
        mimeData.setText(data)
        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.exec_(QtCore.Qt.CopyAction) 
    
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
    
    def itemsToInpOutp(self,items):
        inpItems = []
        outpItems = []
        
        for item in items:
            if isinstance(item,Node):
                if not item.port_in.connections:
                    if item.label:
                        label = item.label.toPlainText()
                        if label in outpItems:#virtual connection
                            outpItems.remove(label)
                        else:
                            n = 1
                            while label in inpItems:
                                label = item.label.toPlainText() + str(n)
                                n += 1
                            inpItems.append(label)
                if not item.port_out.connections:
                    if item.label:
                        label = item.label.toPlainText()
                        if label in inpItems:
                            inpItems.remove(label)
                        else:
                            n = 1
                            while label in outpItems:
                                label = item.label.toPlainText() + str(n)
                                n += 1
                            outpItems.append(label)
                            
        inp = []
        outp = []
        
        for n, value in enumerate(inpItems):
            ypos = -PD*(len(inpItems)-1)/2 + n*PD
            xpos = -(BWmin+PW)/2
            if value:
                name = value
            else:
                name = ''
            inp.append((name,xpos,ypos))
            
        
        for n, value in enumerate(outpItems):
            ypos = -PD*(len(outpItems)-1)/2 + n*PD
            xpos = (BWmin+PW)/2
            if value:
                name = value
            else:
                name = ''
            outp.append((name,xpos,ypos))
        
        return inp,outp
    
    def getSymbolData(self,attributes,properties,parameters):
        name = attributes['name']
        libname = attributes['libname']
        inp = attributes['input']
        outp = attributes['output']
        icon = attributes['icon']
        
#\n\
#def getDiagram():\n\
#    fname = 'libraries.' + libname + '.' + name + '_diagram'\n\
#    exec('import ' + fname)\n\
#    reload(eval(fname))\n\
#\n\
#    items = eval(fname + '.items')\n\
#\n\
#    return items\n\
#\n\
#def getText():\n\
#    fname = 'libraries/' + libname + '/' + name + '.py'\n\
#    f = open(fname,'r')\n\
#    content = f.read()\n\
#    f.close()\n\
#    return content\n\
#\n\
        template = "name = '{name}' #zelfde als bestand naam \n\
libname = '{libname}' #zelfde als map naam\n\
\n\
inp = {inp}\n\
outp = {outp}\n\
\n\
parameters = {parameters} #parametriseerbare cell\n\
properties = {properties} #voor netlisten\n\
\
\
#view variables:\n\
iconSource = '{icon}'\n\
diagramSource = 'libraries/library_{libname}/{name}_diagram.py'\n\
textSource = 'libraries/library_{libname}/{name}.py'\n\
\n\
\n\
views = {{'icon':iconSource,'diagram':diagramSource,'text':textSource}}"
        return template.format(name=name,libname=libname,inp=str(inp),outp=str(outp),properties=str(properties),parameters=str(parameters),icon=str(icon))
        
    
    def convertSymAct(self):
        selection = self.scene.items(self.scene.selectionArea())        
        if selection and self.scene.selectedItems():
            blocks = []
            connections = []
            nodes = []        
            
            for item in selection:
                if isinstance(item,Block):
                    blocks.append(str(item.toPython()))
                if isinstance(item,Connection):
                    connections.append(str(item.toPython()))
                if isinstance(item,Node):
                    nodes.append(str(item.toPython()))
            
                        
            
            dialog = convertSymDialog()
            ret = dialog.getRet()
            if ret:
                inp, outp = self.itemsToInpOutp(selection)            
                
                for item in self.scene.selectedItems():    
                    try:
                        item.remove()
                    except:
                        pass
                name = ret['name']
                icon = ret['icon']
                
                
                if self.library.type == 'symbolView':
                    libname = self.library.tabs.tabText(self.library.tabs.currentIndex())
                else:
                    libname = self.library.libraries.currentItem().text()
                
                attributes = {'name':name,'input':inp,'output':outp,'icon':icon,'libname':libname,'type':'symbol'} 
                        
                
                parameters = dict()
                properties = ret['properties']
                
                data = self.getSymbolData(attributes,properties,parameters)
                
    
                self.path = os.getcwd()            
                f = open(self.path + '/libraries/library_' + libname + '/' + name + '.py','w+')
                f.write(str(data))
                f.close()
                f = open(self.path + '/libraries/library_' + libname + '/' + name + '_diagram.py','w+')
                f.write("blocks = [" + ",\n          ".join(blocks) + "]\n\n" + 
                        "connections = [" + ",\n               ".join(connections) + "]\n\n" + 
                        "nodes = [" + ",\n         ".join(nodes) + "]")
                f.close()
                
                
                
                center = self.scene.getCenter()
                item = libraries.getBlock(name,libname,None,self.scene) 
                item.setPos(center[0],center[1])
                
                if self.library.type == 'symbolView':
                    self.library.symbolView()
                    #self.library.tabs.setCurrentWidget(self.library.symbolTab)
                else:
                    self.library.listView()
                    #self.library.libraries.setCurrentItem(self.library.libraries.findItems('symbols',QtCore.Qt.MatchExactly)[0])
        else:
            error('Select what you want to convert')
    
    def updateAct(self):
        items = self.scene.items()
        for item in items:
            if isinstance(item, Connection):
                self.scene.removeItem(item)
                item.update_path()
            
    
    def getFullFileName(self):
        return(self.path + '/' + self.filename + '.py')

    def askSaving(self,whole=False):
        if whole:
            for i in range(self.centralWidget.count()):              
                items = self.centralWidget.widget(i).scene().items()
                if len(items) != 0:
                    self.centralWidget.setCurrentIndex(i)
                    msg = QtWidgets.QMessageBox()
                    msg.setText('The Document has been modified')
                    msg.setInformativeText('Do you want to save your changes?')
                    msg.setStandardButtons(     QtWidgets.QMessageBox.Question |
                                                QtWidgets.QMessageBox.Save |
                                                QtWidgets.QMessageBox.Discard |
                                                QtWidgets.QMessageBox.Cancel)
                    ret = msg.exec_()
                    if ret == QtWidgets.QMessageBox.Save:
                        self.saveFile()
                    elif ret == QtWidgets.QMessageBox.Cancel:
                        return ret
            return QtWidgets.QMessageBox.Discard
            
            
        else:
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
    def closeTab(self, currentIndex):
        self.centralWidget.setCurrentIndex(currentIndex)
        ret = self.askSaving()
        cancel = False
        if ret == QtWidgets.QMessageBox.Save:
            cancel = self.saveFile()
        if ret != QtWidgets.QMessageBox.Cancel and not cancel:
            self.centralWidget.removeTab(currentIndex)
                 
    def newFile(self,fname=False,symbol=False,blockname=None,libname=None):
        if not fname:
            fname = 'untitled'
        view = GraphicsView(self.centralWidget,symbol)
        if blockname:
            view.blockname = blockname
            view.libname = libname
        view.setMouseTracking(True)
        scene = Scene(self)
        view.setScene(scene)
        view.setRenderHint(QtGui.QPainter.Antialiasing)
        i = self.centralWidget.addTab(view,fname)
        self.centralWidget.setCurrentIndex(i)
#        fname = self.filename
#        try:
#            os.remove(fname+'.py')
#        except:
#            pass
        
#        ret = self.askSaving()
#        cancel = False
#        if ret == QtWidgets.QMessageBox.Save:
#            cancel = self.saveFile()
#        if ret != QtWidgets.QMessageBox.Cancel and not cancel:
#        self.scene.newDgm()
#        self.filename = 'untitled'
#        self.path = os.getcwd()
#        self.setWindowTitle(self.filename)
        
    def openFile(self):
#        fname = self.filename
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
#            ret = self.askSaving()
#            if ret == QtWidgets.QMessageBox.Save:
#                self.saveFile()
#            if ret != QtWidgets.QMessageBox.Cancel:
#                self.scene.newDgm()
            fname = QtCore.QFileInfo(filename)
            self.filename = str(fname.baseName())
            self.path = str(fname.absolutePath())
#            self.setWindowTitle(self.filename)
            self.newFile(self.filename)
            self.scene.loadPython(self.filename,self.path)
    
    def saveFile(self):
        if self.view.symbol:
            instanceName = self.centralWidget.tabText(self.centralWidget.currentIndex())
            symbolName = self.centralWidget.currentWidget().blockname
            libname = self.centralWidget.currentWidget().libname
            exec('import libraries.library_' + libname + '.' + symbolName)
            
            attributes = dict()
            attributes['name'] = eval('libraries.library_' + libname + '.' + symbolName + '.name')
            attributes['libname'] = eval('libraries.library_' + libname + '.' + symbolName + '.libname')
            attributes['icon'] = eval('libraries.library_' + libname + '.' + symbolName + '.iconSource')
                
            
            parameters = eval('libraries.library_' + libname + '.' + symbolName + '.parameters')
            properties = eval('libraries.library_' + libname + '.' + symbolName + '.properties')
            
            blocks = []
            connections = []
            nodes = []        
        
            for item in self.scene.items():
                if isinstance(item,Block):
                    blocks.append(str(item.toPython()))
                if isinstance(item,Connection):
                    connections.append(str(item.toPython()))
                if isinstance(item,Node):
                    nodes.append(str(item.toPython()))
                    
            inp, outp = self.itemsToInpOutp(self.scene.items())        
            
            attributes['input'] = inp
            attributes['output'] = outp
            
            data = self.getSymbolData(attributes,properties,parameters)
            

            self.path = os.getcwd()            
            f = open(self.path + '/libraries/library_' + libname + '/' + symbolName + '.py','w+')
            f.write(str(data))
            f.close()
            f = open(self.path + '/libraries/library_' + libname + '/' + symbolName + '_diagram.py','w+')
            f.write("blocks = [" + ",\n          ".join(blocks) + "]\n\n" + 
                    "connections = [" + ",\n               ".join(connections) + "]\n\n" + 
                    "nodes = [" + ",\n         ".join(nodes) + "]")
            f.close()
            
            if self.library.type == 'symbolView':
                self.library.symbolView()
                #self.library.tabs.setCurrentWidget(self.library.symbolTab)
            else:
                self.library.listView()
                #self.library.libraries.setCurrentItem(self.library.libraries.findItems('symbols',QtCore.Qt.MatchExactly)[0])
            
            
            
            #remove symbol and replace with updated one(keeping pin connections)
            
            for i in range(self.centralWidget.count()):
                tab = self.centralWidget.widget(i)
                if tab.returnSymbol:
                    tab.returnSymbol = False
                    for item in tab.scene().items():
                        if isinstance(item,Block):
                            if item.name == instanceName:
                                pos = item.scenePos()
                                libname = item.libname
                                
                                
                                ports = item.ports()
                                connections = []
                                for port in ports:
                                    connections += port.connections
                                
                                newConn = []
                                
                                for conn in connections:
                                    if conn.port1 in ports:
                                        if isinstance(conn.port1, InPort):
                                            inOrOut = 'in'
                                        else:
                                            inOrOut = 'out'
                                        newConn.append(dict(inOrOut=inOrOut,pos2=conn.pos2,pinlabel=conn.port1.pinlabel.toPlainText()))
                                    elif conn.port2 in ports:
                                        if isinstance(conn.port2, InPort):
                                            inOrOut = 'in'
                                        else:
                                            inOrOut = 'out'
                                        newConn.append(dict(inOrOut=inOrOut,pos1=conn.pos1,pinlabel=conn.port2.pinlabel.toPlainText()))
                                        
                                        
                                item.remove()
                                b = libraries.getBlock(symbolName,libname,scene=tab.scene(),name=instanceName)
                                b.setPos(pos)
                                
                                for nConn in newConn:
                                    conn = Connection(None,tab.scene())
                                    if 'pos1' in nConn:
                                        conn.pos1 = nConn['pos1']
                                        for port in b.ports():
                                            if port.pinlabel.toPlainText() == nConn['pinlabel']:
                                                if (isinstance(port,InPort) and nConn['inOrOut'] == 'in')\
                                                or (isinstance(port,OutPort) and nConn['inOrOut'] == 'out'):
                                                    conn.pos2 = port.scenePos()
                                    else:
                                        conn.pos2 = nConn['pos2']
                                        for port in b.ports():
                                            if port.pinlabel.toPlainText() == nConn['pinlabel']:
                                                if (isinstance(port,InPort) and nConn['inOrOut'] == 'in')\
                                                or (isinstance(port,OutPort) and nConn['inOrOut'] == 'out'):
                                                    conn.pos1 = port.scenePos()
                                    conn.update_ports_from_pos()
#            
            
        else:
            filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save', self.path+'/saves/'+self.filename, filter='*.py')
            if isinstance(filename, tuple):
                    filename = filename[0]
            if filename != '':
                fname = QtCore.QFileInfo(filename)
                self.filename = str(fname.baseName())
                self.path = str(fname.absolutePath())
                self.centralWidget.setTabText(self.centralWidget.currentIndex(),self.filename)
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
            blockname = item.blockname
            libname = item.libname
            flip = item.flip
            icon = item.icon
            libname = item.libname
            inp = dialog.spbInput.value()
            outp = dialog.spbOutput.value()
            
            attributes = {'name':name,'input':inp,'output':outp,'icon':icon,'flip':flip,'libname':libname}            
            parameters = item.parameters
            properties = item.properties
            
            b = Block(attributes,parameters,properties,blockname,libname,None, self.scene)
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
        ret = self.askSaving(whole=True)
#        if ret == QtWidgets.QMessageBox.Save:
#            self.saveFile()
#            Library.closeFlag = True
#            Library.close()
#            event.accept()
#        el
        if ret == QtWidgets.QMessageBox.Discard:

            self.library.closeFlag = True
            self.library.close()
            event.accept()
        else:
            event.ignore()
                
