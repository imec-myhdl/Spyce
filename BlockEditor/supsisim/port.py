#!/usr/bin/python
# aim for python 2/3 compatibility
from __future__ import (division, print_function, unicode_literals)

# Standard library imports
import sys
if sys.version_info >= (3,0):
    basestring = str
from collections import OrderedDict
from autopep8 import fix_code

# Third party imports
from  Qt import QtGui, QtWidgets, QtCore # see https://github.com/mottosso/Qt.py


# Local application imports
from .const import PW, PD, NW, colors
from .dialg import error
from .text  import textItem

class Port(QtWidgets.QGraphicsPathItem):
    """A block holds ports that can be connected to.
    porttype is any of [input, output, inout, ipin, opin, iopin, node]
    labelside is any of [left, right, top, bottom]"""
    def __init__(self, parent, scene, label=None, porttype='node', flip=False):
        if QtCore.qVersion().startswith('5'):
            super(Port, self).__init__(parent)
        else:
            super(Port, self).__init__(parent, scene)
        self.block = None
        self.flip = parent.flip if not parent is None else flip
        self.label_side = 'right'
        self.p = QtGui.QPainterPath()
        self.connections = set()
        self.nodeID = '0'
        self.parent = parent
        self.scene = scene
        if label:
            self.label = textItem(label, parent=self)
        else:
            self.label = None
        self.properties = dict()
        self.signalType = None
        self.setType(porttype.lower())
        self.setup()
        self.setLabel()
        self.setFlip()
        if self not in self.scene.items(): # added since pins/nodes were not auta added in Qt5? 
            self.scene.addItem(self)

    def setup(self):
        self.setPath(self.p)
        if self.porttype in ['ipin', 'opin', 'iopin', 'node']:
            self.setFlag(self.ItemIsSelectable)
            self.setFlag(self.ItemIsMovable)
        else:
            self.setFlag(self.ItemIsSelectable, False)
            self.setFlag(self.ItemIsMovable, False)
        self.setFlag(self.ItemSendsScenePositionChanges)

    def setType(self, porttype=None):
        pp, cc = None, None  # polygon/circle coordinates
        if porttype:
            self.porttype = porttype
            
        if self.porttype is None:
            return
            
        if   self.porttype == 'input': # block input
            pp = ((PW/2,0), (-PW/2,PW/2), (-PW/2,-PW/2))
            self.label_side = 'right'

        elif self.porttype == 'output': # block output
            pp = ((-PW/2,-PW/2), (PW/2,-PW/2), (PW/2,PW/2), (-PW/2,PW/2))
            self.label_side = 'left'

        elif self.porttype == 'inout':  # block inout
            pp = ((-PW/2,0), (0,PW/2), (PW/2,0), (0,-PW/2))
            self.label_side = 'left'

        elif self.porttype == 'ipin': # input terminal
            pp = ((PW/2,0), (0,PW/2), (-PW,PW/2), (-PW,-PW/2), (0,-PW/2))
            self.label_side = 'left'

        elif self.porttype == 'opin': # output terminal
            pp = ((PW/2,0), (0,PW/2), (-PW,PW/2), (-PW/2,0), (-PW,-PW/2), (0,-PW/2))
            self.label_side = 'right'

        elif self.porttype == 'iopin':  # inout terminal
            pp = ((-PW,0), (-PW/2,PW/2), (PW/2,PW/2), (PW,0), (PW/2,-PW/2), (-PW/2,-PW/2))
            self.label_side = 'right'

        elif self.porttype.startswith('node'):  # node
            s = self.porttype[-1].upper()
            self.porttype = 'node'
            d = dict(T='top', B='bottom', L='left', R='right')
            if s in 'TBLR':
                self.label_side = d[s]
            else:
                self.label_side = 'top'
            cc = (-NW/2, -NW/2, NW, NW)

        for k in [self.porttype, 'port_'+self.porttype, self.porttype[:-1]]:
            if k in colors:
                self.lineColor, self.fillColor = colors[k]
                pen = QtGui.QPen(self.lineColor)
                pen.setWidth(1)
                self.setPen(pen)
                self.setBrush(self.fillColor)
                break

        self.p.swap(QtGui.QPainterPath()) # new painterpath
        if pp:
            polygon = QtGui.QPolygonF()
            for (x, y) in pp:
                polygon.append(QtCore.QPointF(x, y))
            polygon.append(QtCore.QPointF(pp[0][0], pp[0][1])) # close polygon
            self.p.addPolygon(polygon)
        elif cc:
            bb = QtCore.QRectF(*cc)
            self.p.addEllipse(bb)

        else:
            error('unknown Port type: {}'.format(self.porttype))
            

    def setLabel(self, label=None, label_side=None):
        if self.label is None:
            if not label in [None, '']:
                self.label = textItem(label, parent=self)
            else:
                return
        elif not label in [None, '']:
            self.label.setText(label)
            
        if label_side:
            self.label_side = label_side
            
        if self.label_side == 'right':
            self.label.setPos(10,0)
            self.label.setAnchor(4)
        elif self.label_side == 'left':
            self.label.setPos(-10,0)
            self.label.setAnchor(6)
        elif self.label_side == 'top':
            self.label.setPos(0,-1)
            self.label.setAnchor(2)
        elif self.label_side == 'bottom':
            self.label.setPos(0,1)
            self.label.setAnchor(8)
        
        self.label.setNormal()
        # pin to block
        if self.porttype in ['input', 'output', 'inout']:
            self.label.setTextInteractionFlags(QtCore.Qt.NoTextInteraction) # disallow edits
            self.label.setFlag(self.ItemIsMovable, False) # do not allow move
            self.label.setFlag(self.ItemIsSelectable, False) # do not allow select
        if self.label.text().startswith('.'):
            self.label.hide()
        else:
            self.label.show()


    def itemChange(self, change, value):
        if change == self.ItemScenePositionHasChanged:
            for conn in self.connections:
                try:
                    conn.update_path()
                except:
                    pass
        return value

    def is_connected(self, other_port):
        for conn in self.connections:
            if conn.port1 == other_port or conn.port2 == other_port:
                return True
        return False

    def remove(self):
        for conn in [c for c in self.connections]:
            try:
                conn.remove()
            except:
                pass
        try:
            self.scene.removeItem(self)
        except AttributeError:
            pass

    def setFlip(self):
        if isPort(self, 'block'): # flip is done via parent (only label needa processing)
            isflipped = self.parent.flip
        else:
            isflipped = self.flip
            if isflipped:
                self.setTransform(QtGui.QTransform.fromScale(-1, 1))
            else:
                self.setTransform(QtGui.QTransform.fromScale(1, 1))

        # check if label is present
        if self.label:
            if isflipped:
                self.label.setFlipped()
            else:
                self.label.setNormal()
                
    def pinToPort(self, inp, outp, inout):
        left, right, top = -80, 80, 20
        name = self.label.text()
        if self.porttype == 'ipin':
            x, y = left, len(inp)*PD
            inp.append( (name, x, y))
        elif self.porttype == 'opin':
            x, y = right, len(outp)*PD
            outp.append( (name, x, y))
        elif self.porttype == 'iopin':
            x, y = len(inout)*PD, top
            inout.append( (name, x, y))
            
    def toData(self):
        data = OrderedDict(type='port')
        data['porttype'] = self.porttype
        data['x'] = self.pos().x()
        data['y'] = self.pos().y()
        if self.flip:
            data['flip'] = self.flip
        if self.label:
            data['label'] = self.label.toData()
        if self.signalType:
            txt = fix_code(self.signalType.text()) # clean up using autopep8
            self.signalType.setText(txt.strip())
            data['signalType'] = self.signalType.toData()
        if self.properties:
            data['properties'] = self.properties
        return data

    def fromData(self, data):
        self.setType(data['porttype'])
        self.setPos(data['x'], data['y'])
        if 'flip' in data:
            self.flip = data['flip']
        if 'label' in data: # do not use setLabel as that would reset the label position
            self.label = textItem('', parent=self)
            self.label.fromData(data['label'])
        if 'signalType' in data:
            self.signalType = textItem('', parent=self)
            self.signalType.fromData(data['signalType'])
            self.signalType.setBrush(colors['signalType'])
        if 'properties' in data:
            self.properties = data['properties']
        self.setup()


def isInPort(item):
    return isinstance(item, Port) and item.porttype in ['input', 'opin', 'iopin']
    
def isOutPort(item):
    return isinstance(item, Port) and item.porttype in ['output', 'ipin', 'iopin']
    
def isInoutPort(item):
    return isinstance(item, Port) and item.porttype in ['inout', 'iopin']

def isPort(item, tp=None):
    if tp == 'block':
        tp = ['input', 'output', 'inout']
    elif tp == 'pin':
        tp = ['ipin', 'opin', 'iopin']
    if isinstance(tp, basestring):
        return isinstance(item, Port) and item.porttype == tp
    elif tp:
        return isinstance(item, Port) and item.porttype in tp
    else:
        return isinstance(item, Port)
        

def isNode(item):
    return isinstance(item, Port) and item.porttype == 'node'
      