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


from supsisim.block import Block, getBlock, getBlockModule
from supsisim.text import isComment
from supsisim.editor import Editor
from supsisim.scene import Scene, GraphicsView
from supsisim.dialg import IO_Dialog, convertSymDialog, viewConfigDialog,error
from supsisim.const import respath, pycmd, PD,PW,BWmin, celltemplate, viewTypes, pythonEditor
from supsisim.port import isInPort, isOutPort, isNode, isPort
from supsisim.connection import isConnection
from supsisim.src_import import import_module_from_source_file
import libraries

DEBUG = False

def strip_ext(fname, ext):
    return fname[:-len(ext)] if fname.endswith(ext) else fname


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
        self.library.diagram_editor = self
        self.runflag = runflag
        if fname != 'untitled':
            self.scene.loadDgm(self.getFullFileName())
            
        self.setWindowTitle('Editor')
        self.status = self.statusBar()
        self.evpos = QtCore.QPointF(0,0)
        self.editor = Editor(self)     
        self.newTab()
        self.editor.install(self.scene)
        self.status.showMessage('Ready')


    def addactions(self):
        mypath = respath + '/icons/'

        self.newFileAction = QtWidgets.QAction(QtGui.QIcon(mypath+'filenew.png'),
                                                '&New', self,
                                                shortcut = 'Ctrl+N',
                                                statusTip = 'New File',
                                                triggered = self.newTab)
        
        self.openFileAction = QtWidgets.QAction(QtGui.QIcon(mypath+'fileopen.png'),
                                                '&Open', self,
                                                shortcut = 'Ctrl+O',
                                                statusTip = 'Open File',
                                                triggered = self.openDiagram)

        self.saveDiagramAction = QtWidgets.QAction(QtGui.QIcon(mypath+'filesave.png'),
                                                '&Save', self,
                                                shortcut = 'Ctrl+S',
                                                statusTip = 'Save File',
                                                triggered = self.saveDiagram)

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
                                             
        self.undoAction = QtWidgets.QAction(QtGui.QIcon(mypath+'undo.png'),
                                             '&Undo',self,
                                             statusTip = 'Undo', 
                                             triggered = self.undo)                                      
                                             
        self.addPinAction = QtWidgets.QAction(QtGui.QIcon(mypath+'AddPin.png'),
                                             '&Add Pin', self,
                                             shortcut = 'N',
                                             statusTip = 'Add Pin',
                                             triggered = self.addPinAct)                                    
        
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

        self.netlistAction = QtWidgets.QAction(QtGui.QIcon(mypath+'codegen.png'),
                                               'Generate netlist',self,
                                               statusTip = 'Generate netlist',
                                               triggered = self.netlistAct)


        self.setBlockAction = QtWidgets.QAction(QtGui.QIcon(mypath+'settings.png'),
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
                                                     
        
#        self.testIndex = QtWidgets.QAction(QtGui.QIcon(mypath+'debug.png'),
#                                             '&Test index',self,
#                                             statusTip = 'Test index',
#                                             triggered = self.testIndexAct) 
        
                                             
    def addToolbars(self):
        toolbarF = self.addToolBar('File')
        toolbarF.addAction(self.newFileAction)
        toolbarF.addAction(self.openFileAction)
        toolbarF.addAction(self.saveDiagramAction)
        toolbarF.addAction(self.printAction)
        toolbarF.addAction(self.exitAction)

        toolbarE = self.addToolBar('Edit')
        toolbarE.addAction(self.copyAction)
        toolbarE.addAction(self.pasteAction)
        toolbarE.addAction(self.convertSymbolAction)
        toolbarE.addAction(self.addPinAction)
        toolbarE.addAction(self.commentAction)
        toolbarE.addAction(self.undoAction)

        toolbarS = self.addToolBar('Simuation')
        toolbarS.addAction(self.runAction)
        toolbarS.addAction(self.codegenAction)
#        toolbarS.addAction(self.setBlockAction)
#        toolbarS.addAction(self.setNetlistAction)
       

        toolbarP = self.addToolBar('Python')
        toolbarP.addAction(self.startPythonAction)
        #toolbarP.addAction(self.testIndex)
        if DEBUG:
            toolbarD = self.addToolBar('Debug')
            toolbarD.addAction(self.debugAction)
    
    def undo(self):
        if len(self.scene.status) > 1:
            x = int(self.view.horizontalScrollBar().value())
            y = int(self.view.verticalScrollBar().value())
            t = self.view.transform()
            fname = self.centralWidget.tabText(self.centralWidget.currentIndex())
            try:
                blockname = self.view.blockname
                libname = self.view.libname            
            except:
                blockname = None
                libname = None
            symbol = self.view.symbol        
                    
            status = self.scene.status
            content = status[-2]       
            
            i = self.centralWidget.currentIndex()
            
            self.newTab(fname,symbol,blockname,libname)
            blocks = []
            connections = []
            nodes = []
            comments = []
            
            for b in content[0]:
                blocks.append(eval(b))
                
            for b in content[1]:
                connections.append(eval(b))
            
            for b in content[2]:
                nodes.append(eval(b))
            
            for b in content[3]:
                comments.append(eval(b))
            self.scene.dataToDiagram(blocks,connections,nodes,comments,False,True)  
            self.scene.status = status[:-2] 
            self.centralWidget.removeTab(i)
            self.view.setTransform(t)
            self.view.horizontalScrollBar().setValue(x)
            self.view.verticalScrollBar().setValue(y)
            
#    def testIndexAct(self):
#        
#        
#        for item in self.scene.items(self.scene.selectionArea()):
#            if isNode(item):
#                if item.label:
#                    error(str(item.label.text()) + str(item.connections) + str(item.connections))
#            if isSegment(item):
#                error(str(item.port1) + str(item.port2))
#                #error(item.port1.parent.label.text())
#            print(item)
#        #point = self.view.mapToScene(self.view.viewport().width()/2,self.view.viewport().height()/2)
#        #print(point.x(),point.y())
            
    def addMenubar(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.openFileAction)
        fileMenu.addAction(self.saveDiagramAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAction)
        
        editMenu = menubar.addMenu('&Edit')
        editMenu.addAction(self.copyAction)
        editMenu.addAction(self.pasteAction)
        editMenu.addAction(self.convertSymbolAction)
        editMenu.addAction(self.undoAction)
#        editMenu.addSeparator()
#        editMenu.addAction(self.updateAction)

        simMenu = menubar.addMenu('&Simulation')
        simMenu.addAction(self.runAction)
        simMenu.addAction(self.codegenAction)
        simMenu.addAction(self.netlistAction)

        setMenu = menubar.addMenu('&Settings')
        setMenu.addAction(self.setBlockAction)
        setMenu.addAction(self.viewConfigAction)
        setMenu.addAction(self.editConstants)
    
    def editSettingsAction(self):
        from supsisim.const import viewTypes
        editor, extension = pythonEditor
        os.system(editor + ' supsisim/const.py')
    
    def viewConfigAct(self):
        dialog = viewConfigDialog()
        ret = dialog.getRet()
        if ret:
            path = os.getcwd()
            fname = '/supsisim/const.py'
            with open(path + fname,'r') as f:
                lines = f.readlines()
            
            for index,line in enumerate(lines):
                if line.startswith('viewEditors = '):
                    del lines[index:]
                    
            for index,view in enumerate(ret):
                if index == 0:
                    string = 'viewEditors = ['
                else:
                    string = "                   "
                string += "dict(type='{}', editor='{}', extension='{}')".format(view['type'],view['editor'],view['extension'])
                if index == len(ret) - 1:
                    string += ']'
                else:
                    string += ',\n'
                lines.append(string)
            
            
            with open(path + fname,'w+') as f:
                f.write("".join(lines))
            f.close()
            
            
            
        
    
    def onChange(self,i):
        self.view=self.centralWidget.widget(i)
        self.scene=self.centralWidget.widget(i).scene()
        self.editor.install(self.scene)
#        for item in self.scene.items():
#            if isinstance(item,Block) and item.type == 'symbol':
#                item.reloadPorts()
#        self.scene.diagramToData('tmp.py')
#        self.scene.newDgm()
#        self.scene.dataToDiagram('tmp',None,False)
#        try:
#            os.remove('tmp.py')
#        except:
#            pass
           
    def descend(self,item):
        self.view.returnSymbol = True
        views = item.getViews()
        if 'diagram' in views:
            diagram = views['diagram']
            fname = os.path.join(libraries.libroot, diagram)
            self.openDiagram(fname)
               
    def ascend(self):
        pass        
    
    def addPinAct(self):
        mimeData = QtCore.QMimeData()
            
        data = 'ipin'
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
                if isinstance(item, Block) or isNode(item):
                    try:
                        item.clone(QtCore.QPointF(200,200))
                    except:
                        pass
                    
#TODO: fix connections
#            for item in self.scene.selection:
#                if isSegment(item):
#                    ports = []
#                    for portItem in self.scene.selection:
#                        if isNode(portItem):
#                            ports.append(portItem)
#                            ports.append(portItem)
#                    if (item.port1 in self.scene.selection or item.port1 in ports) and (item.port2 in ports or item.port2 in self.scene.selection):
#                        try:
#                            c = item.clone(QtCore.QPointF(200,200))
#                            c.update_ports_from_pos()
#                        except:
#                            pass        
    
    def itemsToInpOutp(self,items):
        inpItems = []
        outpItems = []
        
        for item in items:
            if isNode(item):
                if not item.connections:
                    if item.label:
                        label = item.label.text()
                        if label in outpItems:#virtual connection
                            outpItems.remove(label)
                        else:
                            inpItems.append(label)
                if not item.connections:
                    if item.label:
                        label = item.label.text()
                        if label in inpItems:
                            inpItems.remove(label)
                        else:
                            outpItems.append(label)
                            
        #make unique
        for index,inp in enumerate(inpItems):
            inpName = inp
            n = 1
            if inpItems.count(inpName) > 1:
                while inpItems.count(inpName) > 0:
                    inpName = inp + str(n)
                    n += 1
            inpItems[index] = inpName
        for index,outp in enumerate(outpItems):
            outpName = outp
            n = 1
            while outpItems.count(outpName) > 1:
                outpName = outp + str(n)
                n += 1
            outpItems[index] = outpName
                            
                            
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
    
#    def getSymbolData(self,attributes,properties,parameters):
#        name = attributes['name']
#        libname = attributes['libname']
#        inp = attributes['input']
#        outp = attributes['output']
#        io   = attributes['inout'] if 'inout' in attributes else None
#        icon = attributes['icon']
#        views = attributes['views']
#        views['icon'] = icon
#        
#        return celltemplate.format(name = name, 
#                                   libname = libname,
#                                   inp = inp,
#                                   outp = outp,
#                                   io = io,
#                                   bbox = None, 
#                                   properties = properties,
#                                   parameters = parameters,
#                                   views = views)
        
    
    def convertSymAct(self):
        selection = self.scene.items(self.scene.selectionArea())        
        if selection and self.scene.selectedItems():
            # blocks, connections, nodes, comments
            blocks = []
            connections = []
            nodes = []          
            comments = []

            inp = []
            outp = []
            inout = []
            for item in selection:
                if isinstance(item,Block):
                    blocks.append(str(item.toData()))
                elif isConnection(item):
                    connections.append(str(item.toData()))
                elif isNode(item):
                    nodes.append(str(item.toData()))
                elif isPort(item, 'pin'):
                    item.pinToPort(inp, outp, inout)
                elif isComment(item):
                    comments.append(str(item.toData()))
            
                        
            
            dialog = convertSymDialog()
            ret = dialog.getRet()
            
            if ret:

                name = ret['name']
                icon = ret['icon']
                
                
                if self.library.type == 'symbolView':
                    libname = self.library.tabs.tabText(self.library.tabs.currentIndex())
                else:
                    libname = self.library.libraries.currentItem().text()
                                
                ed, ext = viewTypes['diagram']
                views = dict(diagram = os.path.join(libraries.libprefix + libname, name + ext))
                if icon:
                    views['icon'] = icon
                parameters = dict()
                properties = ret['properties']
                
                data = celltemplate.format(name = name, 
                                   libname = libname,
                                   inp = inp,
                                   outp = outp,
                                   io = inout,
                                   bbox = None, 
                                   properties = properties,
                                   parameters = parameters,
                                   views = views)

                # save block
                fname = libraries.blockpath(libname, name)
                with open(fname,'w+') as f:
                    f.write(str(data))

                # save diagram
                ed, ext = viewTypes['diagram']
                fname = strip_ext(fname, '.py') + ext
                self.saveDiagram(fname, selection)

                for item in self.scene.selectedItems():    
                    try:
                        item.remove()
                    except:
                        pass

#                with open(self.path + '/libraries/library_' + libname + '/' + name + '_diagram.py','w+') as f:
#                    f.write("blocks = [" + ",\n          ".join(blocks) + "]\n\n" + 
#                            "connections = [" + ",\n               ".join(connections) + "]\n\n" + 
#                            "nodes = [" + ",\n         ".join(nodes) + "]\n\n" +
#                            "comments = [" + ",\n         ".join(comments) + "]")
                
                
                
                center = self.scene.getCenter()
                item = getBlock(libname,name, None, self.scene) 
                item.setPos(center[0],center[1])
                
                if self.library.type == 'symbolView':
                    self.library.symbolView()
                    self.library.tabs.setCurrentWidget(self.library.symbolTab)
                else:
                    self.library.listView()
                    self.library.libraries.setCurrentItem(self.library.libraries.findItems('symbols',QtCore.Qt.MatchExactly)[0])
        else:
            error('Select what you want to convert')
    
    def updateAct(self):
        items = self.scene.items()
        for item in items:
            if isConnection(item):
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
                        self.saveDiagram()
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
            cancel = self.saveDiagram()
        if ret != QtWidgets.QMessageBox.Cancel and not cancel:
            self.centralWidget.removeTab(currentIndex)
                 
    def newTab(self,fname=False,symbol=False,blockname=None,libname=None):
        view = GraphicsView(self.centralWidget, symbol)
        if blockname:
            view.blockname = blockname
            view.libname = libname
        view.setMouseTracking(True)
        scene = Scene(self)
        view.setScene(scene)
        view.setRenderHint(QtGui.QPainter.Antialiasing)
        if fname:
            i = self.centralWidget.addTab(view, fname)
        else:
            i = self.centralWidget.addTab(view, 'untitled')
        self.centralWidget.setCurrentIndex(i)
        if fname:
            self.openDiagram(fname)
        
#        fname = self.filename
#        try:
#            os.remove(fname+'.py')
#        except:
#            pass
        
#        ret = self.askSaving()
#        cancel = False
#        if ret == QtWidgets.QMessageBox.Save:
#            cancel = self.saveDiagram()
#        if ret != QtWidgets.QMessageBox.Cancel and not cancel:
#        self.scene.newDgm()
#        self.filename = 'untitled'
#        self.path = os.getcwd()
#        self.setWindowTitle(self.filename)
        
    def openDiagram(self, filename=None):
        if filename in [None, False]: 
            filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open', self.path+'/saves/', filter='*.py')
            if isinstance(filename, tuple):
                filename = filename[0]
        if filename:
            path, ffname = os.path.split(filename) # path, full filename
            bname, ext= os.path.splitext(ffname)# basename, extension('.py')
            if ext != '.py':
                return
            self.path = path
            self.filename = bname
            self.newTab(self.filename)
            
            dgm = import_module_from_source_file(os.path.abspath(filename))
            
#            try:
#                blocks      = dgm.blocks
#                nodes       = dgm.nodes
#                connections = dgm.connections
#                comments    = dgm.comments
#                self.scene.dataToDiagram(blocks,connections,nodes,comments)
#
#            except Exception as e:
#                message = 'Error while processing {}\nMessage:{}'.format(os.path.abspath(filename), str(e))
#                error(message)
            blocks      = dgm.blocks
            nodes       = dgm.nodes
            connections = dgm.connections
            comments    = dgm.comments
            self.scene.dataToDiagram(blocks,connections,nodes,comments)

    def saveDiagram(self, filename=None, selection=None):
        ''' saves to diagram. Ask filename if not given. 
        If selected is True only selected elements are written'''
#        if self.view.symbol:
#            instanceName = self.centralWidget.tabText(self.centralWidget.currentIndex())
#            symbolName = self.centralWidget.currentWidget().blockname
#            libname = self.centralWidget.currentWidget().libname
#            exec('import libraries.library_' + libname + '.' + symbolName)
#            
#            blk = libraries.blocks[libname + '/' + symbolName]
#            attributes = dict()
#            attributes['name'] = blk.name
#            attributes['libname'] = blk.libname
#            attributes['icon'] = blk.views['icon']
#            attributes['views'] = blk.views
#            
#            parameters = blk.parameters
#            properties = blk.properties
#            
#            blocks = []
#            connections = []
#            nodes = [] 
#            comments = []
#        
#            for item in self.scene.items():
#                if isinstance(item,Block):
#                    blocks.append(str(item.toData()))
#                if isPort(item, tp=['ipin', 'opin', 'iopin', 'node']):
#                    print(item.porttype)
#                    nodes.append(str(item.toData()))
#                if isinstance(item,textItem):
#                    if item.comment:
#                        comments.append(str(dict(pos=dict(x=item.x(),y=item.y()),text=item.text())))
#                    
#            inp, outp = self.itemsToInpOutp(self.scene.items())        
#            
#            attributes['input'] = inp
#            attributes['output'] = outp
#            
#            data = self.getSymbolData(attributes,properties,parameters)
#            
#
#            self.path = os.getcwd()
#            with open(self.path + '/libraries/library_' + libname + '/' + symbolName + '.py','w+') as f:
#                f.write(str(data))
#
#            with open(self.path + '/libraries/library_' + libname + '/' + symbolName + '_diagram.py','w+') as f:
#                f.write("blocks = [" + ",\n          ".join(blocks) + "]\n\n" + 
#                        "connections = [" + ",\n               ".join(connections) + "]\n\n" + 
#                        "nodes = [" + ",\n         ".join(nodes) + "]\n\n" + 
#                        "comments = [" + ",\n         ".join(comments) + "]")
#            
#            if self.library.type == 'symbolView':
#                self.library.symbolView()
#                #self.library.tabs.setCurrentWidget(self.library.symbolTab)
#            else:
#                self.library.listView()
#                #self.library.libraries.setCurrentItem(self.library.libraries.findItems('symbols',QtCore.Qt.MatchExactly)[0])
#            
#            
#            
#            #remove symbol and replace with updated one(keeping pin connections)
#            
#            for i in range(self.centralWidget.count()):
#                tab = self.centralWidget.widget(i)
#                if tab.returnSymbol:
#                    tab.returnSymbol = False
#                    for item in tab.scene().items():
#                        if isinstance(item,Block):
#                            if item.name == instanceName:
#                                pos = item.scenePos()
#                                libname = item.libname
#                                
#                                
#                                ports = item.ports()
#                                connections = []
#                                for port in ports:
#                                    connections += port.connections
#                                
#                                newConn = []
#                                
#                                for conn in connections:
#                                    if conn.port1 in ports:
#                                        if isInPort(conn.port1):
#                                            inOrOut = 'in'
#                                        else:
#                                            inOrOut = 'out'
#                                        newConn.append(dict(inOrOut=inOrOut,pos2=conn.pos2,pinlabel=conn.port1.pinlabel.text()))
#                                    elif conn.port2 in ports:
#                                        if isOutPort(conn.port2):
#                                            inOrOut = 'in'
#                                        else:
#                                            inOrOut = 'out'
#                                        newConn.append(dict(inOrOut=inOrOut,pos1=conn.pos1,pinlabel=conn.port2.pinlabel.text()))
#                                        
#                                        
#                                item.remove()
#                                b = libraries.getBlock(symbolName,libname,scene=tab.scene(),name=instanceName)
#                                b.setPos(pos)
#                                
#                                for nConn in newConn:
#                                    conn = Segment(None,tab.scene())
#                                    if 'pos1' in nConn:
#                                        conn.pos1 = nConn['pos1']
#                                        for port in b.ports():
#                                            if port.pinlabel.text() == nConn['pinlabel']:
#                                                if (isInPort(port) and nConn['inOrOut'] == 'in')\
#                                                or (isOutPort(port) and nConn['inOrOut'] == 'out'):
#                                                    conn.pos2 = port.scenePos()
#                                    else:
#                                        conn.pos2 = nConn['pos2']
#                                        for port in b.ports():
#                                            if port.pinlabel.text() == nConn['pinlabel']:
#                                                if (isInPort(port) and nConn['inOrOut'] == 'in')\
#                                                or (isOutPort(port) and nConn['inOrOut'] == 'out'):
#                                                    conn.pos1 = port.scenePos()
#                                    conn.update_ports_from_pos()
##            
#            
#        else:
        if filename in [None, False]:
            fname = os.path.join(self.path, 'saves', self.filename + '.py')
            filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save', fname, filter='*.py')
        if filename:
            filename = os.path.abspath(filename)
            self.path, self.filename = os.path.split(filename)
            self.filename, _ = os.path.splitext(self.filename) # strip '.py'
            self.centralWidget.setTabText(self.centralWidget.currentIndex(),self.filename)
            
            blocks, connections, nodes, comments = self.scene.diagramToData(selection)
            with open(filename,'w+') as f:
                f.write('# diagram {}\n'.format(self.filename))
                for s, items in [('blocks',blocks), 
                                 ('connections', connections), 
                                 ('nodes', nodes), 
                                 ('comments', comments)]:
                    jj = ',\n' + ' ' * (len(s) + 4)
                    f.write("\n{} = [{}]\n".format(s, jj.join(items)))
            print('saved file', filename)
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

    def netlistAct(self):
        error('to be implemented')


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
#            self.saveDiagram()
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
                
