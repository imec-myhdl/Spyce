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
from supsisim.text  import textItem, Comment, isTextItem, isComment
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
        self.move = None
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

        self.subMenuText = QtWidgets.QMenu()
        textCloneAction  = self.subMenuText.addAction('Clone')
        textCloneAction.triggered.connect(self.cloneText)
    
        self.subMenuNothing = QtWidgets.QMenu() # right mouse menu when nothing on pos
        nodeInsAction   = self.subMenuNothing.addAction('Insert node')
        nodeInsAction.triggered.connect(self.createNode)

    
    
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
   
    


    def cloneBlock(self):
        item = self.scene.item
        b = item.clone(QtCore.QPointF(100,100))
#        b.name = self.scene.setUniqueName(b)
        b.setup()

    def cloneText(self):
        item = self.scene.item
        c = Comment('')
        c.fromData(item.toData())
        c.setPos(c.pos() + QtCore.QPointF(100,100))
        self.scene.addItem(c)

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
        radius = 4 * DB / self.parent().view.currentscale
        allitems = self.scene.items(QtCore.QRectF(pos-QtCore.QPointF(radius,radius), QtCore.QSizeF(2*radius,2*radius)))
        for item in allitems:
            if isinstance(item, QtWidgets.QGraphicsItem):
                items.append(item)            
                for testfunc in exclude:
                    if testfunc(item):
                        items.pop() # remove
                        break
            if single and items:
                return items[0]
        return items
        
    def sortedItemsAt(self, pos):
        blocks, ports, nodes, connections, labels = [], [], [], [], []
        radius = 4 * DB / self.parent().view.currentscale
        allitems = self.scene.items(QtCore.QRectF(pos-QtCore.QPointF(radius,radius), QtCore.QSizeF(2*radius,2*radius)))
        for item in allitems:
            for cat, test in [(blocks, isBlock), 
                                (nodes, isNode), 
                                (connections, isConnection), 
                                (labels, isTextItem)]:
                if test(item):
                    cat.append(item)
                elif isPort(item): # all ports except nodes
                    ports.append(item)
        return blocks, ports, nodes, connections, labels
        

    def ConnectionAt(self, pos):
        return self.itemAt(pos, exclude=[isNode, isPort, isBlock], single=True)

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
            item.signalType.setBrush(colors['signalType'])
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
            item.setType( dd.pop('Pin_type')[0])
            item.setLabel(dd.pop('Pin_label'))
            if dd:
                item.properties = dd
            item.setup()

    def blockProperties(self):
        item = self.scene.item
        dialog = propertiesDialog(self.scene.mainw, item.properties, addButton=False)
        dd = dialog.getRet()
        if dd:
            item.properties = dd
            self.recreateBlock(item)
    
    def recreateBlock(self, item, scene=None):
        if scene is None:
            scene = self.scene
        pp = dict()
        for port in item.ports():
            portname = port.label.text()
            pp[portname] = []
            for c in port.connections:
                if c.port[0] == port and c.port[1] != port:
                    pp[portname].append((0, c.port[1]))
                elif c.port[0] != port and c.port[1] == port:
                    pp[portname].append((1, c.port[0]))

                    
        data = item.toData() # store blk
        item.remove() # also removes connections
        
        # recreate with new parameters
        par  = item.parameters
        prop = item.properties
        b = getBlock(data['libname'], data['blockname'], scene=scene, 
                     param=par, properties=prop, name=data['blockname'])
        b.fromData(data)
        b.setLabel()
        
        # restore connections to block
        for port in b.ports():
            portname = port.label.text()
            if portname in pp:
                for (ix, p) in pp[portname]:
                    if ix == 0:
                        c = Connection(None, scene, port)
                        c.attach(1, p)
                    else:
                        c = Connection(None, scene, p)
                        c.attach(1, port)
                    c.update_path()
            
    def blockParams(self):
        item = self.scene.item
        dialog = propertiesDialog(self.scene.mainw, item.parameters, addButton=False)
        ret = dialog.getRet()
        if ret:
            # store connections to ports
            item.parameters = ret # apply new parameters (no effect)
            self.recreateBlock(item)


               
        
    def insertConnection(self,event):
        pos = gridPos(event.scenePos())
        item = self.ConnectionAt(pos)
        if item and isConnection(item):
            self.connectionInsertNode(item, pos)

    def createNode(self, pos=None):
        if not isinstance(pos, (QtCore.QPoint, QtCore.QPointF)):
            pos = gridPos(self.event.scenePos())
        newnode = Port(None, self.scene, porttype='node')
        newnode.setPos(pos)
        return newnode


    def connectionStart(self, p):
        self.conn = Connection(None, self.scene, p)
            
    def connectionNext(self, pos):
        newnode = self.createNode(pos)
        self.conn.update_path(newnode) # last point
        self.conn = Connection(None, self.scene, newnode) #new Connection
        
    def connectionFinish(self, port):
        self.conn.update_path(port)
        self.conn = None
        self.scene.mainw.view.setCursor(QtCore.Qt.ArrowCursor)
        self.scene.update()

    def connectionInsertNode(self, conn, pos):
        newnode = self.createNode(pos)
        p = conn.port[1]
        conn.attach(1, newnode)
        conn.update_path()
        newconn = Connection(None, self.scene)
        newconn.attach(0, newnode)
        newconn.attach(1, p)
        newconn.update_path()
        return newconn
        
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
        blocks, ports, nodes, connections, labels = self.sortedItemsAt(pos)
        if self.conn: # connection mode
            while ports: # try to find in-port
                port = ports.pop()
                if isInPort(port):
                    self.connectionFinish(port)
                    return
            while nodes: # else try to find node
                node = nodes.pop()
                self.connectionFinish(node)
                return
#            while connections:
#                conn = connections.pop()
#                if conn != self.conn:
#                    node = self.connectionInsertNode(conn, pos)
#                    self.connectionFinish(node)
#                    return
            self.connectionNext(pos)
                
        else: # not in connection mode
            while ports:
                port = ports.pop()
                if isOutPort(port) and not port.connections:
                    # Try to create new connection starting at selected output port
                    self.connectionStart(port)
                    return

            while nodes:
                node = nodes.pop()

                if node in self.scene.selectedItems():
                    node.setFlag(node.ItemIsMovable)
                else:
                    #starting the connection
                    self.connectionStart(node)
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
            b, p, c, t = [], [], [], []
            for i in self.itemAt(event.scenePos(), single=False):
                if isBlock(i):
                    b.append(i)
                elif isPort(i):
                    p.append(i)
                elif isConnection(i):
                    c.append(i)
                elif isComment(i):
                    t.append(i)
            item = p.pop() if p else b.pop() if b else c.pop() if c else t.pop() if t else None
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
            elif isComment(item):
                self.scene.item = item
                self.event = event
                self.subMenuText.exec_(event.screenPos())
            else:
                self.event = event
                self.subMenuNothing.exec_(event.screenPos())

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


