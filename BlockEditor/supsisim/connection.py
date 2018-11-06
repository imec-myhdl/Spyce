#!/usr/bin/python
# aim for python 2/3 compatibility
from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

from  Qt import QtGui, QtWidgets, QtCore # see https://github.com/mottosso/Qt.py
from collections import OrderedDict

#import sys
#if sys.version_info>(3,0):
#    import sip
#    sip.setapi('QString', 1)

from supsisim.const import LW, colors
from supsisim.port import isPort, isInPort, isOutPort, isNode
from supsisim.node import Node
from supsisim.dialg import error
from lxml import etree

class Connection(QtWidgets.QGraphicsPathItem):
    """Connects one port to another."""

    def __init__(self, parent, scene, p0=None, p1=None):
        if QtCore.qVersion().startswith('5'):
            super(Connection, self).__init__(parent)
            scene.addItem(self)
        else:
            super(Connection, self).__init__(parent, scene)

        self.pos = [None, None]
        self.port = [None, None]
        self.attach(0, p0)
        self.attach(1, p1)
       
        self.label = None
        self.signalType = None

        self.lineColor = colors['connection']

        self.setup()

    def attach(self, ix, p):
        if ix in [0,1]:
            if isPort(p):
                self.pos[ix]  = p.scenePos()
                self.port[ix] = p
                p.connections.add(self)
            elif p:
                self.pos[ix]  = p
                self.port[ix] = None
            # do nothing if p = None
            

    def __str__(self):
        txt  = 'Connection\n'
        txt += 'Position 1 : ' + self.pos[0].__str__() + '\n'
        txt += 'Position 2 : ' + self.pos[1].__str__() + '\n'
        txt += 'Port1 :\n'
        txt += self.port[0].__str__() + '\n'
        txt += 'Port2 :\n'
        txt += self.port[1].__str__() + '\n'
        return txt
    
    def toData(self):
        data = OrderedDict(type='connection')
        data['x0'] = self.pos[0].x()
        data['y0'] = self.pos[0].y()
        data['x1'] = self.pos[1].x()
        data['y1'] = self.pos[1].y()
        if self.label:
            data['label'] = self.label.toPlainText()
        if self.signalType:
            data['signalType'] = self.signalType.toPlainText()
        return data
    
    def setup(self):
        pen = QtGui.QPen(self.lineColor)
        pen.setWidth(LW)
        self.setPen(pen)

    def update_pos_from_ports(self):
        self.pos[0] = self.port[0].scenePos()
        self.pos[1] = self.port[1].scenePos()

#    def update_ports_from_pos(self, undo=False):
#        item = self.scene().find_itemAt(self.pos[0])
##        print('1 ' + str(item))
#        if isOutPort(item) or isNode(item):
#            self.port[0] = item
#        else:
#            if not undo:
#                error("Connection couldn't find pin")
#            self.remove()
#            return
#        item = self.scene().find_itemAt(self.pos[1])
##        print('2 ' + str(item))
#        if isInPort(item)or isNode(item):
#            self.port[1] = item
#        else:
#            if not undo:
#                error("Connection couldn't find pin")
#            self.remove()
#            return
#    
#        self.port[0].connections.append(self)
#        self.port[1].connections.append(self)
#        self.update_path()
        
    def update_path(self, portOrPos=None):
        p = QtGui.QPainterPath()
        if portOrPos:
            self.attach(1, portOrPos)
        item = None
        for ix in [0,1]:
            if self.port[ix]:
                self.pos[ix] = self.port[ix].scenePos()
        if isOutPort(self.port[0]):
            pt = QtCore.QPointF(self.pos[1].x(),self.pos[0].y())
        elif isInPort(self.port[1]) or isInPort(item):
            pt = QtCore.QPointF(self.pos[0].x(),self.pos[1].y())
        else:
            dx = abs(self.pos[1].x()-self.pos[0].x())
            dy = abs(self.pos[1].y()-self.pos[0].y())
            if dx > dy:
                pt = QtCore.QPointF(self.pos[1].x(),self.pos[0].y())
            else:
                pt = QtCore.QPointF(self.pos[0].x(),self.pos[1].y())

        if self.label:
            self.label.setPos(self.pos[1].x(),self.pos[1].y())
        p.moveTo(self.pos[0])
        p.lineTo(pt)
        p.lineTo(self.pos[1])
        self.setPath(p)

    '''
    def paint(self, painter, option, widget):
        pen = QPen()
        pen.setBrush(self.line_color)
        pen.setWidth(LW)
        if self.isSelected():
            pen.setStyle(QtCore.Qt.DotLine)
        painter.setPen(pen)
    '''

    def remove(self):
        try:
            self.port[0].connections.remove(self)
        except (KeyError, AttributeError, ValueError):
            pass
        try:
            self.port[1].connections.remove(self)
        except (KeyError, AttributeError, ValueError):
            pass
        try:
            self.scene().removeItem(self)
        except AttributeError:
            pass

    def clone(self, pt):
        c = Connection(None, self.scene)
        c.pos[0] = self.pos[0].__add__(pt)
        c.pos[1] = self.pos[1].__add__(pt)
        return c
    
    def save(self,root):
        conn = etree.SubElement(root,'connection')
        etree.SubElement(conn,'pos1X').text = self.pos[0].x().__str__()
        etree.SubElement(conn,'pos1Y').text = self.pos[0].y().__str__()
        etree.SubElement(conn,'pos2X').text = self.pos[1].x().__str__()
        etree.SubElement(conn,'pos2Y').text = self.pos[1].y().__str__()

def isConnection(item):
    return isinstance(item, Connection)