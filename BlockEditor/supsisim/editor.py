import sys
#if sys.version_info>(3,0):
#    import sip
#    sip.setapi('QString', 1)

from pyqt45  import QMenu, QGraphicsItem, QtCore, set_orient, QTransform


from supsisim.port import Port, InPort, OutPort
from supsisim.connection import Connection
from supsisim.block import Block
from supsisim.node import Node
from supsisim.dialg import BlockName_Dialog
import supsisim.RCPDlg as pDlg
from supsisim.const import GRID, DB
import numpy as np

class Editor(QtCore.QObject):
    """ Editor to handles events"""
    def __init__(self, parent):
        super(Editor, self).__init__(parent)
        self.conn = None
        self.scene = None
        self.movBlk = False
        self.event = None
        self.connFromNode = False

        self.menuIOBlk = QMenu()
        parBlkAction = self.menuIOBlk.addAction('Block I/Os')
        paramsBlkAction = self.menuIOBlk.addAction('Block Parameters')
        flpBlkAction = self.menuIOBlk.addAction('Flip Block')
        nameBlkAction = self.menuIOBlk.addAction('Change Name')
        cloneBlkAction = self.menuIOBlk.addAction('Clone Block')
        deleteBlkAction = self.menuIOBlk.addAction('Delete Block')
        
        parBlkAction.triggered.connect(self.parBlock)
        flpBlkAction.triggered.connect(self.flpBlock)
        nameBlkAction.triggered.connect(self.nameBlock)
        paramsBlkAction.triggered.connect(self.paramsBlock)
        cloneBlkAction.triggered.connect(self.cloneBlock)
        deleteBlkAction.triggered.connect(self.deleteBlock)

        self.subMenuNode = QMenu()
        nodeDelAction = self.subMenuNode.addAction('Delete node')
        nodeBindAction = self.subMenuNode.addAction('Bind node')
        nodeDelAction.triggered.connect(self.deleteNode)
        nodeBindAction.triggered.connect(self.bindNode)
        
        self.subMenuConn = QMenu()
        connDelAction = self.subMenuConn.addAction('Delete connection')
        connInsAction = self.subMenuConn.addAction('Insert node')
        connDelAction.triggered.connect(self.deleteConn)
        connInsAction.triggered.connect(self.insConn)

    def parBlock(self):
        self.scene.mainw.parBlock()
    
    def flpBlock(self):
        item = self.scene.item
        w = item.label.boundingRect().width()
        if item.flip:
            item.flip = False
            item.setTransform(QTransform.fromScale(1, 1))
            item.label.setTransform(QTransform.fromScale(1,1))
            item.label.setPos(-w/2, item.h/2+5)
        else:
            item.flip = True
            item.setTransform(QTransform.fromScale(-1, 1))
            item.label.setTransform(QTransform.fromTranslate(0,0).scale(-1,1))
            item.label.setPos(w/2, item.h/2+5)


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
        
    def paramsBlock(self):
        item = self.scene.item
        params = item.params.split('|')
        blk = params[0]
        blk = blk.replace('Blk','Dlg')
        if blk in dir(pDlg):
            cmd = 'pDlg.' + blk + '(' + str(item.inp) + ',' + str(item.outp) + ',"' + item.params + '")'
            pars = eval(cmd)
        else:
            pars = pDlg.parsDialog(item.params)
        item.params = pars        

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
            if isinstance(item, QGraphicsItem) and not isinstance(item, Connection):
                return item
        return None
    
    def itemAt(self, pos):
        items = self.scene.items(QtCore.QRectF(pos-QtCore.QPointF(DB,DB), QtCore.QSizeF(2*DB,2*DB)))
        for item in items:
            if isinstance(item, QGraphicsItem):
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
            elif isinstance(item, Connection):
                self.scene.mainw.view.setCursor(QtCore.Qt.PointingHandCursor)
            elif isinstance(item, OutPort):
                self.scene.mainw.view.setCursor(QtCore.Qt.CrossCursor)
            elif isinstance(item, Node):
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
            self.scene.item = item
            self.paramsBlock()
            
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
                        pass
                self.conn = None

            if event.key() == QtCore.Qt.Key_Escape:
                if self.conn != None:
                    self.conn.remove()
                self.conn = None
                self.scene.mainw.view.setCursor(QtCore.Qt.ArrowCursor)
    
        return super(Editor, self).eventFilter(obj, event)

    def gridPos(self, pt):
         gr = GRID
         x = gr * ((pt.x() + gr /2) // gr)
         y = gr * ((pt.y() + gr /2) // gr)
         return QtCore.QPointF(x,y)

