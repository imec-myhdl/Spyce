#!/usr/bin/python
# aim for python 2/3 compatibility
from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

from  Qt import QtWidgets, QtCore # see https://github.com/mottosso/Qt.py

#import sys
#if sys.version_info>(3,0):
#    import sip
#    sip.setapi('QString', 1)

from supsisim.port import Port, InPort, OutPort
from supsisim.connection import Connection
from supsisim.block import Block, textItem
from supsisim.node import Node
from supsisim.dialg import BlockName_Dialog, textLineDialog, overWriteNetlist, error,propertiesDialog
import supsisim.RCPDlg as pDlg
from supsisim.const import GRID, DB
import numpy as np
import libraries
import os.path

class Editor(QtCore.QObject):
    """ Editor to handles events"""
    def __init__(self, parent):
        super(Editor, self).__init__(parent)
        self.conn = None
        self.scene = None
        self.movBlk = False
        self.event = None
        self.connFromNode = False

        self.menuIOBlk = QtWidgets.QMenu()
        #parBlkAction = self.menuIOBlk.addAction('Block I/Os')
        paramsBlkAction = self.menuIOBlk.addAction('Block Parameters')
        propertiesBlkAction = self.menuIOBlk.addAction('Block Properties')
        flpBlkAction = self.menuIOBlk.addAction('Flip Block')
        nameBlkAction = self.menuIOBlk.addAction('Change Name')
        cloneBlkAction = self.menuIOBlk.addAction('Clone Block')
        deleteBlkAction = self.menuIOBlk.addAction('Delete Block')
        netListAction = self.menuIOBlk.addAction('Netlist')
        
        #parBlkAction.triggered.connect(self.parBlock)
        flpBlkAction.triggered.connect(self.flpBlock)
        nameBlkAction.triggered.connect(self.nameBlock)
        paramsBlkAction.triggered.connect(self.paramsBlock)
        propertiesBlkAction.triggered.connect(self.propertiesBlock)
        cloneBlkAction.triggered.connect(self.cloneBlock)
        deleteBlkAction.triggered.connect(self.deleteBlock)
        netListAction.triggered.connect(self.netList)

        self.subMenuNode = QtWidgets.QMenu()
        nodeDelAction = self.subMenuNode.addAction('Delete node')
        nodeBindAction = self.subMenuNode.addAction('Bind node')
        nodeLabelAction = self.subMenuNode.addAction('Add/Edit label')
        nodeDelAction.triggered.connect(self.deleteNode)
        nodeBindAction.triggered.connect(self.bindNode)
        nodeLabelAction.triggered.connect(self.addNodeLabel)
        
        self.subMenuConn = QtWidgets.QMenu()
        connDelAction = self.subMenuConn.addAction('Delete connection')
        connInsAction = self.subMenuConn.addAction('Insert node')
        connLabelAction = self.subMenuConn.addAction('Add/Edit label')
        connTypeAction = self.subMenuConn.addAction('Add/Edit signal type')
        connDelAction.triggered.connect(self.deleteConn)
        connInsAction.triggered.connect(self.insConn)
        connLabelAction.triggered.connect(self.addConnLabel)
        connTypeAction.triggered.connect(self.addConnType)
    

    
    def netList(self):
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
                content = supsisim.netlist.netlist(item.blockname,item.libname,item.properties)
                print(fname)
                f = open(fname,'w+')
                f.write(content)
                f.close()
                if not 'myhdl' in views:
                    self.addView(item.blockname,item.libname,'myhdl')
                self.parent().library.openView('myhdl',item)
        else:
            error("file doesn't have a diagram")
        
    def addView(self,blockname,libname,type):
        import os
        path = os.getcwd()
        fname = '/libraries/library_{}/{}.py'.format(libname,blockname)
        f = open(path + fname,'r')
        lines = f.readlines()
        f.close()
        
        for index,line in enumerate(lines):
            if line.startswith('iconSource = '):
                source = "{type}Source = 'libraries/library_{libname}/{blockname}_{type}.py'\n"
                lines.insert(index+1,source.format(type=type,libname=libname,blockname=blockname))
            if line.startswith('views = {'):
                lines[index] = line.replace('views = {',"views = {{'{type}':{type}Source,".format(type=type))
        
        
        f = open(path + fname,'w+')
        f.write("".join(lines))
        f.close()
    
    def addConnType(self):
        item = self.scene.item
        if item.signalType:
            dialog = textLineDialog('Signal type: ','Signal type',item.signalType.toPlainText())
        else:
            dialog = textLineDialog('Signal type: ','Signal type')
        ret = dialog.getLabel()
        if ret:
            item.signalType = textItem(ret, anchor=3, parent=item)
            item.signalType.setPos(item.pos2.x(),item.pos2.y())
    
    def addNodeLabel(self):
        item = self.scene.item
        if item.label:
            dialog = textLineDialog('Label: ',content=item.label.toPlainText())
        else:
            dialog = textLineDialog('Label: ')
        ret = dialog.getLabel()
        if ret:
            if item.label:
                item.label.setPlainText(ret)
            else:
                item.label = textItem(ret, anchor=3, parent=self.scene.item)
                item.label.setPos(0,20)
    
    def addConnLabel(self):
        conn = self.scene.item
        if conn.label:
            dialog = textLineDialog('Label: ',content=conn.label.toPlainText())
        else:
            dialog = textLineDialog('Label: ')
        ret = dialog.getLabel()
        if ret:
            if conn.label:
                conn.label.setPlainText(ret)
            else:
                conn.label = textItem(ret, anchor=3, parent=conn)
                conn.label.setPos(conn.pos2.x(),conn.pos2.y())
        
    def parBlock(self):
        self.scene.mainw.parBlock()
    
    def flpBlock(self):
        item = self.scene.item
        item.flip = not item.flip
        item.setFlip()

    def nameBlock(self):
        item = self.scene.item
        dialog = BlockName_Dialog(self.scene.mainw)
        dialog.name.setText(item.name)
        res = dialog.exec_()
        if res == 1:
            item.name = str(dialog.name.text())
            item.label.setPlainText(item.name)
            w = item.label.boundingRect().width()
            item.label.setPos(-w/2, item.h/2+5)    
        
    def propertiesBlock(self):
        item = self.scene.item
        dialog = propertiesDialog(item.properties)
        ret = dialog.getRet()
        if ret:
            item.properties = ret      
            
    def paramsBlock(self):
        item = self.scene.item
        dialog = propertiesDialog(item.parameters,False)
        ret = dialog.getRet()
        if ret:
            block = item.toPython()
            item.remove()
            b = libraries.getBlock(block['blockname'],block['libname'],scene=self.scene,param=ret,name=block['name'])
            b.setPos(block['pos']['x'],block['pos']['y'])
            b.properties = block['properties']

    def cloneBlock(self):
        item = self.scene.item
        item.clone(QtCore.QPointF(100,100))


    def deleteBlock(self):
        item = self.scene.item
        item.remove()
        
    def deleteNode(self):
        self.scene.item.remove()

    def bindNode(self):
        item = self.scene.item
        if len(item.port_out.connections) == 1:
            c1 = item.port_in.connections[0]
            c2 = item.port_out.connections[0]
            c = Connection(None, self.scene)
            c.pos1 = c1.pos1
            c.pos2 = c2.pos2
            item.remove()
            c.update_ports_from_pos()
            if isinstance(c.port1, OutPort) and isinstance(c.port2, InPort):
                pos = QtCore.QPointF((c.pos2.x()+c.pos1.x())/2, c.pos1.y()) 
                self.newNode(c, pos)                            

    def deleteConn(self):
        self.scene.item.remove()

    def insConn(self):
        if not self.conn:
            self.insertConnection(self.event)
 
    def install(self, scene):
        scene.installEventFilter(self)
        self.scene = scene

    def connectionAt(self, pos):
        items = self.scene.items(QtCore.QRectF(pos-QtCore.QPointF(4*DB,4*DB), QtCore.QSizeF(8*DB,8*DB)))
        for item in items:
            if isinstance(item, Connection):
                return item
        return None

    def blockAt(self, pos):
        items = self.scene.items(QtCore.QRectF(pos-QtCore.QPointF(DB,DB), QtCore.QSizeF(2*DB,2*DB)))
        for item in items:
            if isinstance(item, QtWidgets.QGraphicsItem) and not isinstance(item, Connection):
                return item
        return None
    
    def itemAt(self, pos):
        items = self.scene.items(QtCore.QRectF(pos-QtCore.QPointF(DB,DB), QtCore.QSizeF(2*DB,2*DB)))
        for item in items:
            if isinstance(item, QtWidgets.QGraphicsItem):
                if isinstance(item,Node):
                    pass
                return item
        return None

    def newNode(self, item, pos):
        port2 = item.port2
        pos2 = item.pos2
        c = Connection(None, self.scene)
        b = Node(None, self.scene)
        b.setPos(pos)
        item.port2.connections.remove(item)
        item.port2.connections.append(c)
        item.port2 = b.port_in
        item.port2.connections.append(item)
        item.pos2 = b.pos()
        c.port1 = b.port_out
        c.port2 = port2
        c.port1.connections.append(c)
        c.pos1 = b.pos()
        c.pos2 = pos2
        item.update_path()
        c.update_path()
        self.scene.isInsConn = False
        self.scene.isConnecting = True
        
    def insertConnection(self,event):
        item = self.connectionAt(event.scenePos())
        if item and isinstance(item, Connection):
            self.newNode(item, event.scenePos())

    def genInterPoint(self):
        p1 = self.conn.pos1
        p2 = self.conn.pos2
        item = self.blockAt(p2)

        if isinstance(self.conn.port1, OutPort):
            pt = QtCore.QPointF(p2.x(),p1.y())
        elif isinstance(item, InPort):
            pt = QtCore.QPointF(p1.x(),p2.y())
        else:
            dx = np.abs(p2.x() - p1.x())
            dy = np.abs(p2.y() - p1.y())
            if dx > dy:
                pt = QtCore.QPointF(p2.x(),p1.y())
            else:
                pt = QtCore.QPointF(p1.x(),p2.y())
        return pt

    def moveMouse(self, obj, event):
        if self.connFromNode:
            return
        item = self.itemAt(event.scenePos())
        if self.conn:
            self.scene.mainw.view.setCursor(QtCore.Qt.ArrowCursor)
            if item and isinstance(item, InPort):
                if len(item.connections) == 0:
                    self.scene.mainw.view.setCursor(QtCore.Qt.CrossCursor)
                else:
                    self.scene.mainw.view.setCursor(QtCore.Qt.ArrowCursor)
            elif item and isinstance(item, Node):
                if len(item.port_in.connections) == 0:
                    self.scene.mainw.view.setCursor(QtCore.Qt.CrossCursor)
                else:
                    self.scene.mainw.view.setCursor(QtCore.Qt.ArrowCursor)
            self.conn.pos2 = event.scenePos()
            self.conn.update_path()
            #return True
        else:
            if isinstance(item, Block):
                items = self.scene.selectedItems()
            
                for item in items:                                           
                    if isinstance(item, Block):
                        for thing in item.childItems():
                            if isinstance(thing, InPort):
                                if len(thing.connections) != 0:
                                    conn = thing.connections[0]
                                    nd = conn.port1.parent
                                    if isinstance(nd, Node):
                                        pt = QtCore.QPointF(nd.pos().x(), item.pos().y()+thing.pos().y())
                                        nd.setPos(pt)
                                        conn.update_pos_from_ports()
                                        conn.update_path()                        
                                            
                        for thing in item.childItems():
                            if isinstance(thing, OutPort):
                                if len(thing.connections) != 0:
                                    conn = thing.connections[0]
                                    nd = conn.port2.parent
                                    if isinstance(nd, Node):
                                        pt = QtCore.QPointF(nd.pos().x(), item.pos().y()+thing.pos().y())
                                        nd.setPos(pt)
                                        conn.update_pos_from_ports()
                                        conn.update_path()
            #elif isinstance(item, Connection):
                #self.scene.mainw.view.setCursor(QtCore.Qt.PointingHandCursor)
            elif isinstance(item, OutPort):
                self.scene.mainw.view.setCursor(QtCore.Qt.CrossCursor)
            elif isinstance(item, Node):
                if item in self.scene.selectedItems():
                    self.scene.mainw.view.setCursor(QtCore.Qt.PointingHandCursor)
                else:
                    self.scene.mainw.view.setCursor(QtCore.Qt.CrossCursor)
            else:
                self.scene.mainw.view.setCursor(QtCore.Qt.ArrowCursor)
                

    def mouseLeftButtonPressed(self, obj, event):
        item = self.blockAt(event.scenePos())
        if self.conn:
            if isinstance(item, Node):
                # Try to connect to Node
                if item.port_in.connections == []:
                    self.conn.port2 = item.port_in
                    self.conn.pos2 = item.scenePos()                               
                    self.conn.port1.connections.append(self.conn)
                    self.conn.port2.connections.append(self.conn)                            
                    self.conn.update_path()
                    self.conn = None
            elif isinstance(item,InPort):
                # Try to finish connection to a Port
                if len(item.connections) == 0:
                    self.conn.port2 = item
                    self.conn.pos2 = item.scenePos()
                    self.conn.port1.connections.append(self.conn)
                    self.conn.port2.connections.append(self.conn)
                    self.conn.update_path()
                    if isinstance(self.conn.port1, OutPort):
                        pos = QtCore.QPointF((self.conn.pos2.x()+self.conn.pos1.x())/2, self.conn.pos1.y()) 
                        self.newNode(self.conn, pos)
                    self.conn = None
                    self.scene.mainw.view.setCursor(QtCore.Qt.ArrowCursor)
            else:
                # Generate a new node and continue drawing connections
                pt = self.genInterPoint()
                b = Node(None, self.scene)
                b.setPos(pt)
                self.conn.port2 = b.port_in
                self.conn.pos2 = b.scenePos()
                self.conn.port1.connections.append(self.conn)
                self.conn.port2.connections.append(self.conn)
                self.conn.update_path()
                
                self.conn = Connection(None, self.scene)
                self.conn.port1 = b.port_out
                self.conn.pos1 = b.scenePos()
                self.conn.pos2 = b.scenePos()        

        else:
            if item and isinstance(item, OutPort):
                # Try to create new connection starting at selected output port
                if len(item.connections) == 0:
                    self.conn = Connection(None, self.scene)
                    self.conn.port1 = item
                    self.conn.pos1 = item.scenePos()
                    self.conn.pos2 = item.scenePos()
            elif item and isinstance(item, Node):
                # Try to create new connection starting at selected node
                if item in self.scene.selectedItems():
                    #selected the node to move it
                    for item in self.scene.selectedItems():
                        if isinstance(item,Node):
                            item.setFlag(item.ItemIsMovable)
                else:
                    #starting the connection
                    self.conn = Connection(None, self.scene)
                    self.connFromNode = True
                    self.conn.port1 = item.port_out
                    self.conn.pos1 = item.scenePos()
                    self.conn.pos2 = item.scenePos()

    def mouseRightButtonPressed(self, obj, event):
        if self.conn == None:
            item = self.itemAt(event.scenePos())
            if isinstance(item, Block):
                self.scene.item = item
                self.scene.evpos = event.scenePos()
                self.menuIOBlk.exec_(event.screenPos())
            elif isinstance(item, Node):
                self.scene.item = item
                self.subMenuNode.exec_(event.screenPos())
            elif isinstance(item, Connection):
                self.scene.item = item
                self.event = event
                self.subMenuConn.exec_(event.screenPos())
            else:
                pass

    def mouseReleased(self, obj, event):
        if self.connFromNode:
            self.connFromNode = False
        items = self.scene.selectedItems()
        for item in items:                   
            if isinstance(item, Block) or isinstance(item, Node):
                item.setPos(item.scenePos())
                for thing in item.childItems():
                    if isinstance(thing, Port):
                        for conn in thing.connections:
                            conn.update_pos_from_ports()

    def mouseDoubleClicked(self, obj, event):
        item = self.blockAt(event.scenePos())
        if isinstance(item, Block):
            if item.hasDiagram():
                self.scene.mainw.descend(item)
            
    def eventFilter(self, obj, event):
        if event.type() ==  QtCore.QEvent.GraphicsSceneMouseMove:
             self.moveMouse(obj, event)

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
                            if item.comment:
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

    def gridPos(self, pt):
         gr = GRID
         x = gr * ((pt.x() + gr /2) // gr)
         y = gr * ((pt.y() + gr /2) // gr)
         return QtCore.QPointF(x,y)

