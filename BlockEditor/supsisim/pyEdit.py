
# aim for python 2/3 compatibility
from __future__ import (division, print_function, absolute_import,
                        unicode_literals)
from builtins import str
from builtins import range

import sys, traceback

from  Qt import QtGui, QtWidgets, QtCore # see https://github.com/mottosso/Qt.py
from  Qt.QtPrintSupport import QPrinter, QPrintDialog

import os
from collections import OrderedDict
#if sys.version_info>(3,0):
#    import sip
#    sip.setapi('QString', 1)


from .block import Block, getBlock, getBlockModule, isBlock, gridPos
from .text import isComment, textItem, Comment
from .editor import Editor
from .scene import Scene, GraphicsView
from .dialg import IO_Dialog, convertSymDialog, viewConfigDialog, error, fileDialog
from .const import respath, pycmd, PD,PW,BWmin, templates, viewTypes, pythonEditor
from .port import Port, isInPort, isOutPort, isNode, isPort
from .connection import isConnection, Connection
from .src_import import import_module_from_source_file
from .netlist import netlist
import libraries

DEBUG = False

def strip_ext(fname, ext):
    return fname[:-len(ext)] if fname.endswith(ext) else fname

def d2s(d):
    '''dict to string'''
    items = []
    for k, v in list(d.items()):
        if k != 'type': # suppress 'type' attributes
            if isinstance(v, (dict, OrderedDict)):
                items.append('{}={}'.format(k, d2s(v)))
            else:
                items.append('{}={}'.format(k, repr(v)))
    return 'dict({})'.format(', '.join(items))


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
        self.setStyleSheet('''QTextEdit { font-size: 10pt}''')    


    def addactions(self):
        mypath = respath + '/icons/'

        self.newFileAction = QtWidgets.QAction(QtGui.QIcon(mypath+'filenew.png'),
                                                '&New', self,
                                                shortcut = 'Ctrl+N',
                                                statusTip = 'New File',
                                                triggered = self.newTab)
        
        self.openFileAction = QtWidgets.QAction(QtGui.QIcon(mypath+'fileopen.png'),
                                                '&Open Diagram', self,
                                                shortcut = 'Ctrl+O',
                                                statusTip = 'Open File',
                                                triggered = self.openDiagram)

        self.saveDiagramAction = QtWidgets.QAction(QtGui.QIcon(mypath+'filesave.png'),
                                                '&Save', self,
                                                shortcut = 'Ctrl+S',
                                                statusTip = 'Save File',
                                                triggered = self.saveDiagram)

        self.saveDiagramAsAction = QtWidgets.QAction(QtGui.QIcon(mypath+'filesave.png'),
                                                '&Save As', self,
                                                statusTip = 'Save File As',
                                                triggered = self.saveDiagramAs)

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

#        self.importPinsAction = QtWidgets.QAction('&Import pins',self,
#                                             statusTip = 'Import pins from block', 
#                                             triggered = self.importPins)                                      
#
                                             
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

        # self.codegenAction = QtWidgets.QAction(QtGui.QIcon(mypath+'codegen.png'),
        #                                        'Generate C-code',self,
        #                                        statusTip = 'Generate C-Code',
        #                                        triggered = self.codegenAct)

        self.netlistMyhdlAction = QtWidgets.QAction(QtGui.QIcon(mypath+'codegen.png'),
                                               'Generate mydhl netlist',self,
                                               statusTip = 'Generate mydhl netlist',
                                               triggered = self.netlistMyhdlAct)


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

        # toolbar Edit
        toolbarE = self.addToolBar('Edit')
        toolbarE.addAction(self.copyAction)
        toolbarE.addAction(self.pasteAction)
        toolbarE.addAction(self.convertSymbolAction)
        toolbarE.addAction(self.addPinAction)
        toolbarE.addAction(self.commentAction)
        toolbarE.addAction(self.undoAction)
#        toolbarE.addAction(self.importPinsAction)

        # toolbar Simulate
        toolbarS = self.addToolBar('Simuation')
        toolbarS.addAction(self.runAction)
        toolbarS.addAction(self.netlistMyhdlAction)

        # toolbar Python
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
            self.dataToDiagram(blocks,connections,nodes,comments,False,True)  
            self.scene.status = status[:-2] 
            self.centralWidget.removeTab(i)
            self.view.setTransform(t)
            self.view.horizontalScrollBar().setValue(x)
            self.view.verticalScrollBar().setValue(y)

#    def importPins(self):
#        try:
#            blockname = self.view.blockname
#            libname = self.view.libname
#            blk = getBlockModule(libname, blockname)
#            
#            inp = blk.inp if hasattr(blk, 'inp') else []
#            outp = blk.outp if hasattr(blk, 'outp') else []
#            io = blk.io if hasattr(blk, 'io') else []
#            pins = dict()
#            for (pname, x, y) in inp:
#                pins[pname] = ('inp', x, y)
#            for (pname, x, y) in outp:
#                pins[pname] = ('outp', x, y)
#            for (pname, x, y) in io:
#                pins[pname] = ('io', x, y)
#                
#            print()     
#                
#            
#        except AttributeError:
#            pass
        
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
        fileMenu.addAction(self.saveDiagramAsAction)
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
        # simMenu.addAction(self.codegenAction)
        simMenu.addAction(self.netlistMyhdlAction)

        setMenu = menubar.addMenu('&Settings')
        setMenu.addAction(self.setBlockAction)
        setMenu.addAction(self.viewConfigAction)
        setMenu.addAction(self.editConstants)
    
    def editSettingsAction(self):
        from supsisim.const import viewTypes
        editor, extension = pythonEditor
        os.system(editor + ' settings.py')
    
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
            
    def update_blocks(self, libname=None, blockname=None):
        for i in range(self.centralWidget.count()):
            scene = self.centralWidget.widget(i).scene()
            for item in list(scene.items()):
                if isBlock(item):
                    if libname and item.libname != libname:
                        continue
                    if blockname and item.blockname != blockname:
                        continue
                    self.editor.recreateBlock(item, scene)
    
    def onChange(self,i):
        self.view=self.centralWidget.widget(i)
        self.scene=self.centralWidget.widget(i).scene()
        if hasattr(self.centralWidget.widget(i), 'fname'):
            self.filename = self.centralWidget.widget(i).fname
        self.editor.install(self.scene)
#        for item in self.scene.items():
#            if isinstance(item,Block) and item.type == 'symbol':
#                item.reloadPorts()
#        self.diagramToData('tmp.py')
#        self.scene.newDgm()
#        self.dataToDiagram('tmp',None,False)
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
            block_tr = dict()
            port_tr = dict()
            conn_list  = []
            dx, dy = 100, 100
            for item in self.scene.selection:
                newitem = None
                if isinstance(item, Block):
                    b = item.clone(QtCore.QPointF(dx,dy))
                    b.setSelected(True)
                    block_tr[item.label.text()] = b
                elif isConnection(item):
                    conn_list.append(item)
                elif isPort(item, 'pin') or isPort(item, 'node'):
                    newitem = Port(None, self.scene)
                    port_tr[item] = newitem
                elif isComment(item):
                    newitem = Comment('')
                    self.scene.addItem(newitem)
#                else:
#                    print ('skipping paste of ', item.toData())

                item.setSelected(False)
                if newitem:
                    data = item.toData()
                    data['x'] += dx
                    data['y'] += dy
                    newitem.fromData(data)
                    newitem.setSelected(True)
            
            for c in conn_list:
                data = c.toData()
                conn = Connection(None, scene=self.scene)
                conn.pos[0] = QtCore.QPointF(data['x0']+dx, data['y0']+dy)
                conn.pos[1] = QtCore.QPointF(data['x1']+dx, data['y1']+dy)
                for ix, p in [(0, 'p0'), (1, 'p1')]:
                    if p in data: # translate blocknames
                       (blkname, pinname) = data[p] # update to new blockname
                       if blkname in block_tr:
                           b = block_tr[blkname]
                           conn.attach(ix, b.ports(retDict=True)[pinname])
                    elif c.port[ix]:
                        port = c.port[ix]
                        if port in port_tr:
                            conn.port[ix] = port_tr[port]
                conn.update_path()

 
 #                    self.editor.movBlk = gridPos(QtCore.QPointF((left+right)/2, (top+bottom)/2))

                    
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
                
                data = templates['block'].format(name = name, 
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
                self.saveDiagramAs(fname, selection)

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
                    ix = self.library.tabs.currentIndex()
                    self.library.symbolView()
                    self.library.tabs.setCurrentIndex(ix)
                else:
                    self.library.listView()
                    self.library.libraries.setCurrentItem(self.library.libraries.findItems('symbols',QtCore.Qt.MatchExactly)[0])
        else:
            error('Select what you want to convert')
    
    def updateAct(self):
        items = list(self.scene.items())
        for item in items:
            if isConnection(item):
                self.scene.removeItem(item)
                item.update_path()
            
    
    def getFullFileName(self):
        return(self.path + '/' + self.filename + '.py')

    def askSaving(self,whole=False):
        if whole:
            for i in range(self.centralWidget.count()):              
                items = list(self.centralWidget.widget(i).scene().items())
                fname = self.centralWidget.widget(i).fname
                if len(items) != 0:
                    self.centralWidget.setCurrentIndex(i)
                    msg = QtWidgets.QMessageBox()
                    msg.setText('{} has been modified'.format(os.path.basename(fname)))
                    msg.setInformativeText('Do you want to save your changes?')
                    msg.setStandardButtons(     QtWidgets.QMessageBox.Question |
                                                QtWidgets.QMessageBox.Save |
                                                QtWidgets.QMessageBox.Discard |
                                                QtWidgets.QMessageBox.Cancel)
                    ret = msg.exec_()
                    if ret == QtWidgets.QMessageBox.Save:
                        self.saveDiagramAs()
                    elif ret == QtWidgets.QMessageBox.Cancel:
                        return ret
            return QtWidgets.QMessageBox.Discard
            
            
        else:
            items = list(self.scene.items())
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
            cancel = self.saveDiagramAs()
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
            self.centralWidget.widget(i).fname = 'untitled'
        self.centralWidget.setCurrentIndex(i)
#        if fname:
#            self.openDiagram(fname)
        
#        fname = self.filename
#        try:
#            os.remove(fname+'.py')
#        except:
#            pass
        
#        ret = self.askSaving()
#        cancel = False
#        if ret == QtWidgets.QMessageBox.Save:
#            cancel = self.saveDiagramAs()
#        if ret != QtWidgets.QMessageBox.Cancel and not cancel:
#        self.scene.newDgm()
#        self.filename = 'untitled'
#        self.path = os.getcwd()
#        self.setWindowTitle(self.filename)
        
    def openDiagram(self, filename=None):
        if filename in [None, False]:
            filename = fileDialog(self, 'Open Diagram', self.path, filter='Diagram (*.py *.diagram);;All (*.*)')

            if isinstance(filename, tuple):
                filename = filename[0]
        if filename:
            path, ffname = os.path.split(filename) # path, full filename
            bname, ext= os.path.splitext(ffname)# basename, extension('.py')
            ed, dgmext = viewTypes['diagram']
            if ext not in ['.py', dgmext]:
                error(filename + ' is not a diagram')
                return
            self.path = path
            self.filename = bname
            self.newTab(self.filename)

            ix = self.centralWidget.currentIndex()
            self.centralWidget.widget(ix).fname = filename # store name
            
            dgm = import_module_from_source_file(os.path.abspath(filename))
            
            blocks      = dgm.blocks
            nodes       = dgm.nodes
            connections = dgm.connections
            comments    = dgm.comments
            self.dataToDiagram(blocks,connections,nodes,comments)


    def saveDiagram(self):
        ix = self.centralWidget.currentIndex()
        filename = self.centralWidget.widget(ix).fname
        self.saveDiagramAs(filename)

    def saveDiagramAs(self, filename=None, selection=None):
        ''' saves to diagram. Ask filename if not given. 
        If selected is True only selected elements are written'''
        if filename in [None, False]:
            ix = self.centralWidget.currentIndex()
            fname = self.centralWidget.widget(ix).fname
#            fname = os.path.join(self.path, 'saves', self.filename)
            filename = fileDialog(self, 'Save Diagram', filename=fname, filter='Diagram (*.py *.diagram);;All (*.*)')
            print (filename)


        if filename:
            fn, ext = os.path.splitext(filename)
            print ('filename', fn, '; ext', ext)
            if ext not in [viewTypes['diagram'][1], '.py']: # add extension if missing
                filename += viewTypes['diagram'][1]
            filename = os.path.abspath(filename)
            ix = self.centralWidget.currentIndex()
            self.centralWidget.widget(ix).fname = filename # store full path
            self.path, self.filename = os.path.split(filename)
            self.filename, _ = os.path.splitext(self.filename) # strip '.py'
            self.centralWidget.setTabText(ix, self.filename)
            
            blocks, connections, nodes, comments = self.diagramToData(selection)
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

    def diagramToData(self, selection=None):
        blocks = []
        connections = []
        nodes = []        
        comments = []
        for block in self.scene.blocks: # force unique names
            block.setLabel(verbose=True)
        items = selection if selection else list(self.scene.items())
        for item in items:
            if isBlock(item):
                d = item.toData()
                if d:
                    blocks.append(d2s(d))
            elif isConnection(item):
                d = item.toData()
                if d:
                    connections.append(d2s(d))
            elif isPort(item, tp=['ipin', 'opin', 'iopin', 'node']):
                d = item.toData()
                if d:
                    nodes.append(d2s(d))
            elif isComment(item):
                d = item.toData()
                if d:
                    comments.append(d2s(d))
                    
        return (blocks, connections, nodes, comments)
        
    def dataToDiagram(self, blocks, connections, nodes, comments, center=True, undo=False):
        errors = []
        
        for data in blocks:
            prop = data['properties'] if 'properties' in data else dict()
            if 'parameters' in data:
                #getBlock(libname, blockname, parent=None, scene=None, param=dict(), name=None, flip=False)
                b = getBlock(data['libname'], data['blockname'], scene=self.scene,
                             param=data['parameters'], properties=prop, errors=errors)
            else: 
                b = getBlock(data['libname'], data['blockname'], scene=self.scene, 
                             properties=prop , errors=errors)
                
            if b:
                b.fromData(data)
                    
        for item in nodes:
            try:
                pos = QtCore.QPointF(item['x'], item['y'])
            except KeyError:
                print('skipping malmormed node. Save again to clean up.')
                continue
            if self.scene.find_itemAt(pos):
                print('discarding overlapping node at x={}, y={}'.format(item['x'], item['y']))
            else:
                p = Port(None, self.scene)
                p.fromData(item)

        for data in connections:
            try:
                pos = [QtCore.QPointF(data['x0'], data['y0'])]
                pos.append(QtCore.QPointF(data['x1'], data['y1']))
            except KeyError:
                print('skipping malmormed connection. Save again to clean up.')
                continue
            if pos[0] == pos[1]:
                print('discarding zero length segment x={}, y={}'.format(data['x0'], data['y0']))
            else:
                conn = Connection(None, self.scene)
                for ix in [0,1]:
                    port = self.scene.find_itemAt(pos[ix], exclude=(Block, Connection, textItem))
                    if isPort(port):
                        conn.attach(ix, port)
                    else:
                        conn.pos[ix] = pos[ix]
                        print('no port at ', pos[ix])
                conn.update_path()
                        
                if 'label' in data:
                    conn.label = textItem(data['label'], anchor=3, parent=conn)
                    conn.label.setPos(conn.pos2.x(),conn.pos2.y())
                if 'signalType' in data:
                    conn.signalType = textItem(data['signalType'], anchor=3, parent=conn)
                    conn.signalType.setPos(conn.pos2.x(),conn.pos2.y())

        for data in comments:
            comment = Comment('')
            comment.fromData(data)
            self.scene.addItem(comment)

        if center:
            self.scene.mainw.view.centerOn(self.scene.getCenter()[0],self.scene.getCenter()[1])
            
        if errors:
            error('\n'.join(errors))

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

    def netlistMyhdlAct(self):
        ix = self.centralWidget.currentIndex()
        fname = self.centralWidget.widget(ix).fname
        dirname, basename = os.path.split(fname)
        dgmname, ext = os.path.splitext(basename)
        netlist_dir = os.path.join(os.curdir, 'netlist_myhdl', dgmname)
        
        #actual netlisting
#        netlist(fname, lang='myhdl', netlist_dir=netlist_dir)
        try:
            netlist(fname, lang='myhdl', netlist_dir=netlist_dir)
            # print message
            b = QtWidgets.QMessageBox()
            b.setWindowModality(QtCore.Qt.ApplicationModal)
            b.setText('netlist written in ' + netlist_dir)
            b.exec_()

        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            ee = traceback.format_tb(exc_traceback)
            error('netlisting of {} produced error:\n\nStacktrace:\n{}\nError message:\n{}'.format(fname, ''.join(ee), str(e)))
        


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
#            self.saveDiagramAs()
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
                
