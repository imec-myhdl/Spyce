#!/usr/bin/python
# aim for python 2/3 compatibility
from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

from  Qt import QtWidgets, QtCore # see https://github.com/mottosso/Qt.py

#import sys
#if sys.version_info>(3,0):
#    import sip
#    sip.setapi('QString', 1)

import os
from collections import OrderedDict

from supsisim.port import Port, isInPort, isOutPort, isPort, isNode
from supsisim.connection import Connection, isConnection
from supsisim.block import isBlock, gridPos, getBlock
from supsisim.text  import textItem, isComment, isTextItem
from supsisim.dialg import BlockName_Dialog, textLineDialog, overWriteNetlist, \
                           error, propertiesDialog
import supsisim.RCPDlg as pDlg
from supsisim.const import DB, colors
import libraries

class Editor(QtCore.QObject):
    """ Editor to handles events"""
    def __init__(self, parent):
        super(Editor, self).__init__(parent)
        self.conn = None
        self.scene = None
        self.status = parent.status
        self.movBlk = False
        self.event = None
        self.connFromNode = False

        self.menuIOBlk = QtWidgets.QMenu()
        #parBlkAction = self.menuIOBlk.addAction('Block I/Os')
        paramsBlkAction = self.menuIOBlk.addAction('Parameters')
        propertiesBlkAction = self.menuIOBlk.addAction('Properties')
        flpBlkAction = self.menuIOBlk.addAction('Flip')
        nameBlkAction = self.menuIOBlk.addAction('Change Name')
        cloneBlkAction = self.menuIOBlk.addAction('Clone Block')
        deleteBlkAction = self.menuIOBlk.addAction('Delete Block')        
#        self.netlistMenu = QtWidgets.QMenu('Netlist')
#        self.menuIOBlk.addMenu(self.netlistMenu)
#        netListAction = self.menuIOBlk.addAction('Netlist')
        
        #parBlkAction.triggered.connect(self.parBlock)
        flpBlkAction.triggered.connect(self.flipBlock)
        nameBlkAction.triggered.connect(self.nameBlock)
        paramsBlkAction.triggered.connect(self.blockParams)
        propertiesBlkAction.triggered.connect(self.blockProperties)
        cloneBlkAction.triggered.connect(self.cloneBlock)
        deleteBlkAction.triggered.connect(self.deleteBlock)
#        netListAction.triggered.connect(self.netList)

        self.subMenuPort = QtWidgets.QMenu()
        portEditAction = self.subMenuPort.addAction('Edit')
        portFlipAction = self.subMenuPort.addAction('Flip')
        portDelAction  = self.subMenuPort.addAction('Delete')
        portTypeAction  = self.subMenuPort.addAction('Add/Edit signal type')
        portEditAction.triggered.connect(self.portEdit)
        portFlipAction.triggered.connect(self.flipBlock)
        portDelAction.triggered.connect(self.portDelete)
        portTypeAction.triggered.connect(self.portAddType)
        
        
        self.subMenuConn = QtWidgets.QMenu()
        connDelAction   = self.subMenuConn.addAction('Delete connection')
        connInsAction   = self.subMenuConn.addAction('Insert node')
        connLabelAction = self.subMenuConn.addAction('Add/Edit label')
        connDelAction.triggered.connect(self.deleteConn)
        connInsAction.triggered.connect(self.insConn)
        connLabelAction.triggered.connect(self.addConnLabel)
    

    
    
    def addConnLabel(self):
        conn = self.scene.item
        if conn.label:
            dialog = textLineDialog('Label: ',content=conn.label.text())
        else:
            dialog = textLineDialog('Label: ')
        ret = dialog.getLabel()
        if ret:
            if conn.label:
                conn.label.setText(ret)
            else:
                conn.label = textItem(ret, anchor=3, parent=conn)
                conn.label.setPos(conn.pos2.x(),conn.pos2.y())

    
    
#    def addView(self,blockname,libname,type):
#        error('fix me: addView in editor.py')
#        return
#        path = os.getcwd()
#        fname = '/libraries/library_{}/{}.py'.format(libname,blockname)
#        f = open(path + fname,'r')
#        lines = f.readlines()
#        f.close()
#        
#        for index,line in enumerate(lines):
#            if line.startswith('iconSource = '):
#                source = "{type}Source = 'libraries/library_{libname}/{blockname}_{extension}'\n"
#                from supsisim.const import viewEditors
#                for viewEditor in viewEditors:
#                    if type == viewEditor['type']:
#                        extension = viewEditor['extension']
#                source = source.format(type=type,libname=libname,blockname=blockname,extension = extension)
#                lines.insert(index+1,source)
#            if line.startswith('views = {'):
#                lines[index] = line.replace('views = {',"views = {{'{type}':{type}Source,".format(type=type))
#        
#        
#        f = open(path + fname,'w+')
#        f.write("".join(lines))
#        f.close()

    def cloneBlock(self):
        item = self.scene.item
        b = item.clone(QtCore.QPointF(100,100))
#        b.name = self.scene.setUniqueName(b)
        b.setup()

    def ConnectionAt(self, pos):
        items = self.scene.items(QtCore.QRectF(pos-QtCore.QPointF(4*DB,4*DB), QtCore.QSizeF(8*DB,8*DB)))
        for item in items:
            if isConnection(item):
                return item
        return None

    def deleteBlock(self):
        item = self.scene.item
        item.remove()
        
    def portDelete(self):
        self.scene.item.remove()

    def deleteConn(self):
        self.scene.item.remove()

        
    def flipBlock(self):
        item = self.scene.item
        item.flip = not item.flip
        item.setFlip()

    def insConn(self):
        if not self.conn:
            self.insertConnection(self.event)
 
    def install(self, scene):
        scene.installEventFilter(self)
        self.scene = scene

    def itemAt(self, pos, exclude=[], single=True):
        items = []
        for item in self.scene.items(QtCore.QRectF(pos-QtCore.QPointF(DB,DB), QtCore.QSizeF(2*DB,2*DB))):
            if isinstance(item, QtWidgets.QGraphicsItem):
                items.append(item)            
                for testfunc in exclude:
                    if testfunc(item):
                        items.pop() # remove
                        break
            if single and items:
                return items[0]
        return items

    def nameBlock(self):
        item = self.scene.item
        dialog = BlockName_Dialog(self.scene.mainw)
        dialog.name.setText(item.name)
        res = dialog.exec_()
        if res == 1:
#            item.name = str(dialog.name.text())
            item.setLabel(dialog.name.text())
#            item.label.setNormal()
#            w = item.label.boundingRect().width()
#            item.label.setPos(-w/2, item.h/2+5)    

        self.scene.isInsConn = False
        self.scene.isConnecting = True

    def netList(self,type):
        try:
            item = self.scene.item
            fname = 'libraries.library_{}.{}'.format(item.libname,item.blockname)
            exec('import ' + fname)
            func = eval(fname + '.netlist' + type)
            func(item)
            
        except:
            if type == 'myhdl':
                item = self.scene.item
            
                if item.hasDiagram():
                    views = libraries.getViews(item.blockname,item.libname)
                    fname = 'libraries/library_{}/{}_myhdl.py'.format(item.libname,item.blockname)
                    overwrite = True            
                    if 'myhdl' in views:
                        dialog = overWriteNetlist()
                        ret = dialog.exec_()
                        if ret == 0:
                            fname = views['myhdl']
                        else:
                            overwrite = False
                    if overwrite:
                        import supsisim.netlist
                        content = supsisim.netlist.netlistMyHdl(item.blockname,item.libname,item.properties)
                        if content == False:
                            error('More than 1 label on signal')
                            return
                        f = open(fname,'w+')
                        f.write(content)
                        f.close()
                        if not 'myhdl' in views:
                            self.addView(item.blockname,item.libname,'myhdl')
                        self.parent().library.openView('myhdl',item)
                else:
                    error("file doesn't have a diagram")
            else:
                error('netlist not found')
                
    def parBlock(self):
        self.scene.mainw.parBlock()
    
    def portAddType(self, event):
        item = self.scene.item
        if not isPort(item):
            error('use on nodes/pins')
            return
        if item.signalType:
            dialog = textLineDialog('Signal type: ','Signal type',item.signalType.text())
        else:
            dialog = textLineDialog('Signal type: ','Signal type')
        ret = dialog.getLabel()
        if ret:
            item.signalType = textItem(ret, anchor=8, parent=item)
            self.signalType.setBrush(colors['signalType'])
            font = item.signalType.font()
            font.setItalic(True)
            item.signalType.setFont(font)

#            item.signalType.setPos(item.pos2.x(),item.pos2.y())
        
    def portEdit(self):
        item = self.scene.item
        if not isPort(item):
            error('not a pin')
        dd = OrderedDict()
        dd['Pin_label'] = item.label.text() if item.label else ''
        
        options = 'ipin opin iopin node'.split()
        dd['Pin_type'] = (item.porttype, options)
        properties = item.properties
        title = 'Edit Node' if isNode(item) else 'Edit Pin'
        dialog = propertiesDialog(self.scene.mainw, dd, properties, title=title)
        dd = dialog.getRet()
        if dd:
            item.setType( dd['Pin_type'])
            item.setLabel(dd['Pin_label'])
            item.properties = dd['properties']
            print (dd['properties'])
            item.setup()

    def blockProperties(self):
        item = self.scene.item
        dialog = propertiesDialog(self.scene.mainw, item.properties, addButton=True)
        dd = dialog.getRet()
        if dd:
           item.properties = dd   
            
    def blockParams(self):
        item = self.scene.item
        dialog = propertiesDialog(self.scene.mainw, item.parameters, addButton=False)
        ret = dialog.getRet()
        if ret:
            block = item.toData()
            item.remove()
            b = getBlock(block['blockname'],block['libname'],scene=self.scene,param=ret,name=block['name'])
            b.setPos(block['pos']['x'],block['pos']['y'])
            b.properties = block['properties']



    
        
    def insertConnection(self,event):
        pos = gridPos(event.scenePos())
        item = self.ConnectionAt(pos)
        if item and isConnection(item):
            self.connectionInsertNode(item, pos)



    def connectionStart(self, p):
        self.conn = Connection(None, self.scene, p)
            
    def connectionNext(self, pos):
        newnode = Port(None, self.scene, porttype='node')
        newnode.setPos(pos)
        self.conn.update_path(newnode) # last point
        self.conn = Connection(None, self.scene, newnode) #new Connection
        
    def connectionFinish(self, port):
        self.conn.update_path(port)
        self.conn = None
        self.scene.mainw.view.setCursor(QtCore.Qt.ArrowCursor)
        self.scene.update()

    def connectionInsertNode(self, conn, pos):
        newnode = Port(None, self.scene, porttype='node')
        newnode.setPos(pos)
        p = conn.port[1]
        conn.update_path(newnode) # last point
        newconn = Connection(None, self.scene, newnode)
        newconn.update_path(p)
        
    def addNetlistMenu(self):
        blockname = self.scene.item.blockname
        libname = self.scene.item.libname
        fname = 'libraries.library_{}.{}'.format(libname,blockname)
        exec('import ' + fname) in globals(),locals()
        reload(eval(fname))
        attributes = dir(eval(fname))
        netlistFunctions = []
        for attribute in attributes:
            if attribute.startswith('netlist'):
                netlistFunctions.append(attribute.replace('netlist',''))
        if not 'myhdl' in netlistFunctions:
            netlistFunctions.append('myhdl')
        for type in netlistFunctions:
            def getFunction(type):
                def netlistAction():
                    self.netList(type)
                return netlistAction
            netlistAction = getFunction(type)
            action = self.netlistMenu.addAction(type+" netlist")
            action.triggered.connect(netlistAction)

    def mouseDoubleClicked(self, obj, event):
        pos = gridPos(event.scenePos())
        item = self.itemAt(pos, exclude=[isConnection])
        if isBlock(item):
            if 'diagram' in item.getViews():
                self.scene.mainw.descend(item)
        elif isPort(item, tp='ipin opin iopin node'.split()):
            self.scene.item = item
            self.portEdit()
            if self.conn:
                self.conn.remove()
                self.conn = None
                self.scene.mainw.view.setCursor(QtCore.Qt.ArrowCursor)
        elif isTextItem(item):
            font, ok = QtWidgets.QFontDialog.getFont(item.font())
            if ok:
                item.setFont(font)
            
    def mouseLeftButtonPressed(self, obj, event):
        pos = gridPos(event.scenePos())
        items = self.itemAt(pos, single=False, )
        if self.conn: # connection mode
            while True: # continue until either empty, or Port/Node found
                if len(items) == 0:
                    self.connectionNext(pos)
                    return
                item = items.pop()
                if isNode(item): # connect to node
                    self.connectionFinish(item)
                    break
                elif isInPort(item):
                    if len(item.connections) == 0: # connect to free port
                        self.connectionFinish(item)
                        break
                
        elif items: # not in connection mode
            while len(items) > 0:
                item = items.pop(0)
                if isOutPort(item):
                    # Try to create new connection starting at selected output port
                    if len(item.connections) == 0:
                        self.connectionStart(item)
                elif isNode(item):
                    # Try to create new connection starting at selected node
                    if item in self.scene.selectedItems():
                        #selected the node to move it
                        for item in self.scene.selectedItems():
                            if isNode(item):
                                item.setFlag(item.ItemIsMovable)
                    else:
                        #starting the connection
                        self.connectionStart(item)
                        self.connFromNode = True

    def moveMouse(self, obj, event):
        if self.connFromNode:
            return
        pos = gridPos(event.scenePos())    
        item = self.itemAt(pos)
        
        if self.conn:
            self.scene.mainw.view.setCursor(QtCore.Qt.ArrowCursor)
            if item and isInPort(item) or isNode(item):
                if len(item.connections) == 0:
                    self.scene.mainw.view.setCursor(QtCore.Qt.CrossCursor)
                else:
                    self.scene.mainw.view.setCursor(QtCore.Qt.ArrowCursor)
            elif item and isNode(item):
                if len(item.connections) == 0:
                    self.scene.mainw.view.setCursor(QtCore.Qt.CrossCursor)
                else:
                    self.scene.mainw.view.setCursor(QtCore.Qt.ArrowCursor)
            self.conn.update_path(pos)
            #return True
        elif item:
            if isBlock(item):
                items = self.scene.selectedItems()
            
                for item in items:                                           
                    if isBlock(item):
                        for thing in item.childItems():
                            if isPort(thing, 'block'):
                                for conn in thing.connections:
                                        conn.update_path()                        
                                            
            #elif isConnection(item):
                #self.scene.mainw.view.setCursor(QtCore.Qt.PointingHandCursor)
            elif isOutPort(item):
                self.scene.mainw.view.setCursor(QtCore.Qt.CrossCursor)
            elif isNode(item):
                if item in self.scene.selectedItems():
                    self.scene.mainw.view.setCursor(QtCore.Qt.PointingHandCursor)
                else:
                    self.scene.mainw.view.setCursor(QtCore.Qt.CrossCursor)
            else:
                self.scene.mainw.view.setCursor(QtCore.Qt.ArrowCursor)
                

    def mouseReleased(self, obj, event):
        self.connFromNode = False
        items = self.scene.selectedItems()
        for item in items:                   
            if isBlock(item) or isPort(item) or isComment(item):
                item.setPos(gridPos(item.pos()))
                for thing in item.childItems():
                    if isPort(thing, 'block'):
                        for conn in thing.connections:
                            conn.update_path()

    def mouseRightButtonPressed(self, obj, event):
        if self.conn == None:
            b, p, c = [], [], []
            for i in self.itemAt(event.scenePos(), single=False):
                if isBlock(i):
                    b.append(i)
                elif isPort(i):
                    p.append(i)
                elif isConnection(i):
                    c.append(i)
            item = p.pop() if p else b.pop() if b else c.pop() if c else None
            if isBlock(item):
                self.scene.item = item
#                self.netlistMenu.clear()
#                self.addNetlistMenu()
                self.menuIOBlk.exec_(event.screenPos())
            elif isPort(item, ['node', 'ipin', 'opin','iopin']):
                self.scene.item = item
                self.subMenuPort.exec_(event.screenPos())
            elif isConnection(item):
                self.scene.item = item
                self.event = event
                self.subMenuConn.exec_(event.screenPos())
            else:
                pass

    def eventFilter(self, obj, event):
        if event.type() ==  QtCore.QEvent.GraphicsSceneMouseMove:
             self.moveMouse(obj, event)
             self.status.showMessage('{:.1f}, {:.1f}'.format(event.scenePos().x(), event.scenePos().y()))
             
        elif event.type() ==  QtCore.QEvent.GraphicsSceneMousePress:
            if event.button() == QtCore.Qt.LeftButton:
                self.mouseLeftButtonPressed(obj, event)
            elif event.button() == QtCore.Qt.RightButton:
                self.mouseRightButtonPressed(obj, event)

        elif event.type() == QtCore.QEvent.GraphicsSceneMouseRelease:
            self.mouseReleased(obj, event)
                
        elif event.type() == QtCore.QEvent.GraphicsSceneMouseDoubleClick:
            self.mouseDoubleClicked(obj, event)
                
        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Delete:
                items = self.scene.selectedItems()
                for item in items:
                    try:
                        item.remove()
                    except:
                        try:
                            if isComment(item):
                                self.scene.removeItem(item)
                        except:
                            pass
                if self.conn:
                    self.conn.remove()
                #self.conn = None

            if event.key() == QtCore.Qt.Key_Escape:
                if self.conn != None:
                    self.conn.remove()
                self.conn = None
                self.scene.mainw.view.setCursor(QtCore.Qt.ArrowCursor)
            if event.key() == QtCore.Qt.Key_Control:
                self.scene.mainw.view.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        if event.type() == QtCore.QEvent.KeyRelease and event.key() == QtCore.Qt.Key_Control:
            self.scene.mainw.view.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        return super(Editor, self).eventFilter(obj, event)


