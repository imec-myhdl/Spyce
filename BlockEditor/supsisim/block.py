#!/usr/bin/python
# aim for python 2/3 compatibility
from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

from  Qt import QtGui, QtWidgets, QtCore # see https://github.com/mottosso/Qt.py

import sys, os, ast
#if sys.version_info>(3,0):
#    import sip
#    sip.setapi('QString', 1)

#import sip
from lxml import etree

import libraries
from supsisim.port import Port, InPort, OutPort
from supsisim.const import GRID, PW, LW, BWmin, BHmin, PD, respath, qtpinlabels





class Block(QtWidgets.QGraphicsPathItem):
    """A block holds ports that can be connected to."""
    def __init__(self,attributes,parameters,properties,blockname,libname,parent=None,scene=None,):
        self.scene = scene
        if QtCore.qVersion().startswith('5'):
            super(Block, self).__init__(parent)
            if self.scene:
                self.scene.addItem(self)
        else:
            super(Block, self).__init__(parent, self.scene)
        
        self.blockname = blockname
        self.libname = libname
        self.name = attributes.pop('name')
        self.inp = attributes.pop('input')
        self.outp = attributes.pop('output')
        self.icon = attributes.pop('icon')
        self.flip = attributes.pop('flip') if 'flip' in attributes else False
        self.type = attributes.pop('type') if 'type' in attributes else 'Block'
        self.libname = attributes.pop('libname')
        self.height = attributes.pop('height') if 'height' in attributes else 0
        
        self.parameters = parameters
        self.properties = properties
        
        self.line_color = QtCore.Qt.black
        self.fill_color = QtCore.Qt.black
        if self.scene:
            self.setup()
            
#    def __init__(self,old=True, *args, **kwargs):
#        if len(args) >= 2:
#            parent, self.scene = args[0], args[1]
#        elif len(args) == 1:
#            parent, self.scene = None, args[0]
#        else:
#            parent, self.scene = None, None
#        if QtCore.qVersion().startswith('5'):
#            super(Block, self).__init__(parent)
#            if self.scene:
#                self.scene.addItem(self)
#        else:
#            super(Block, self).__init__(parent, self.scene)
#        if len(args) == 9:
#            parent, self.scene, self.name, self.inp, self.outp, self.iosetble, self.icon, self.params, self.flip = args
#        elif len(args) == 3:
#            parent, self.scene, strBlk = args
#            ln = strBlk.split('@')
#            self.name   = str(ln[0])
#            self.inp    = ast.literal_eval(ln[1]) # ast.literal_eval is a lot safer than 'eval'
#            self.outp   = ast.literal_eval(ln[2])
#            self.icon   = str(ln[4])
#            self.params = str(ln[5])
#            self.flip   = False
#            io          = int(ln[3])
#            iosetble = (io==1)
#            self.iosetble = iosetble
#        elif len(args) <= 2:
#            self.name     = kwargs.pop('name')     if 'name' in kwargs else ''
#            self.inp      = kwargs.pop('inp')      if 'inp' in kwargs else 0
#            self.outp     = kwargs.pop('outp')     if 'outp' in kwargs else 0
#            self.icon     = kwargs.pop('icon')     if 'icon' in kwargs else ''
#            self.params   = kwargs.pop('params')   if 'params' in kwargs else ''
#            self.flip     = kwargs.pop('flip')     if 'flip' in kwargs else False
#            self.iosetble = kwargs.pop('iosetble') if 'iosetble' in kwargs else False
#            x             = float(kwargs.pop('x')) if 'x' in kwargs else 0.0
#            y             = float(kwargs.pop('y')) if 'y' in kwargs else 0.0
#            self.setPos(x, y)
#            self.flip     = kwargs.pop('flip')     if 'flip' in kwargs else False
##            self.__dict__.update(kwargs) # update the block attributes, maybe a bit dangerous
#        else:
#            raise ValueError('Needs 9 or 3 arguments; received %i.' % len(args))
#        
#        self.line_color = QtCore.Qt.black
#        self.fill_color = QtCore.Qt.black
#        if self.scene:
#            self.setup()
            
    def from_txt(s):
        '''convert text to int or list'''
        
    def __str__(self):
        txt  = 'Name         :' + self.name.__str__() +'\n'
        txt += 'Input ports  :' + self.inp.__str__() + '\n'
        txt += 'Output ports :' + self.outp.__str__() + '\n'
        txt += 'Icon         :' + self.icon.__str__() + '\n'
        txt += 'Properties       :' + self.properties.__str__() + '\n'
        for thing in self.childItems():
            print(thing)
        return txt
        
    def __repr__(self):
        return str(self.toPython())
    
    
    def toPython(self):
        data = dict(labelPos=dict(x=self.label.x(),y=self.label.y()),
                    properties=self.properties,type='block',
                    name=self.label.toPlainText(),
                    blockname=self.blockname,
                    libname=self.libname,
                    pos=dict(x=self.x(),y=self.y()))
        if self.parameters:
            data['parameters'] = self.parameters
        return data
    
#    def toPython(self, lib=False):
#        fmt = 'Block({kwargs})'
#        fields = 'name inp outp icon parameters properties views'.split()
#        kwargs = []
#        x, y, flip = int(self.x()), int(self.y()), self.flip
#        if not lib: # add x, y, flip for schematic(diagrams)
#            if x:
#                fields.append('x')
#            if y:
#                fields.append('y')
#            if flip:
#                fields.append('flip')
#        for k in fields:
#            if k in self.__dict__:
#                v = self.__dict__[k]
#            else:
#                v = eval(k)
#            if v:
#                kwargs.append('{}={}'.format(k, repr(v)))
#
#        return fmt.format(kwargs=', '.join(kwargs))
    
    def hasDiagram(self):
        fname = 'libraries.library_' + self.libname + '.' + self.blockname
        exec('import ' + fname)
        reload(eval(fname))
        if 'diagram' in eval(fname + '.views'):
            return True
        else:
            return False
        
    def setup(self,scene=True):
        self.ports_in = []
        self.name = self.scene.setUniqueName(self) if scene else self.blockname
        if isinstance(self.inp, int):
            Ni = self.inp  if isinstance(self.inp, int) else len(self.inp)
            No = self.outp if isinstance(self.outp, int) else len(self.outp)
            Nports = max(Ni, No)
            self.w = BWmin
            self.h = BHmin+PD*(max(Nports-1,0))
            self.leftOffset = -self.w/2
            self.topOffset = -self.h/2
        else:
            # find bounding box
            x0, y0, x1, y1 = None, None, None, None
            for item in self.inp + self.outp:
                x0 = item[1] if x0 == None else min(x0, item[1])
                x1 = item[1] if x1 == None else max(x1, item[1])
                y0 = item[2] if y0 == None else min(y0, item[2])
                y1 = item[2] if y1 == None else max(y1, item[2])
                #print(y0,y1,y,self.name)
            if x0 != None and x1 != None:
                self.leftOffset = min(x0+PW/2,-BWmin/2)
                self.w = - self.leftOffset + max(x1 -PW/2,BWmin/2)
            else:
                self.w = BWmin
                self.leftOffset = -self.w/2
                
                
            if y0 != None and y1 != None:
                self.topOffset = min(y0-PD/2,-BHmin/2)
                self.h = - self.topOffset + max(y1 + PD/2,BHmin/2)
            else:
                self.h = BHmin
                self.topOffset = - self.h/2
                
                
#            self.w = max(BWmin - PW, x1-x0 - PW) if x1 != None and x0 != None else BWmin# + PD
#            self.leftOffset = min(x0,-BWmin/2) + self.w/2 + PW/2 if x0 != None else 0
#            #print(BHmin,y1 - y0 + PD,self.name)
#            self.h = max(BHmin + PD, y1 - y0 + PD) if y1 != None and y0 != None else BHmin # block height
#            self.topOffset = min(y0,-BHmin/2) + self.h/2 - PD/2 if y0 != None else 0

        self.h = max(self.h,self.height)
        p = QtGui.QPainterPath()
        
        p.addRect(self.leftOffset, self.topOffset, self.w, self.h)

        self.setPath(p)
 
        if isinstance(self.inp, int):
            for n in range(0,self.inp): # legacy: self.inp is integer number
                self.add_inPort(n)
        else:
            for n in self.inp: # new: self.inp is list of tuples (name, x,y)
                self.add_inPort(n)

        if isinstance(self.outp, int):
            for n in range(0,self.outp):# legacy: self.out = integer number
                self.add_outPort(n)
        else:
            for n in self.outp: # new: self.outp is list of tuples (name, x,y)
                self.add_outPort(n)
                
        self.label = textItem(self.name, anchor=8, parent=self)
        self.label.setPos(0, self.topOffset + self.h)

#        self.label = QGraphicsTextItem(self)
#        self.label.setPlainText(self.name)
#        w = self.label.boundingRect().width()
#        if self.flip:
#            self.setTransform(QTransform.fromScale(-1,1))
#            self.label.setTransform(QTransform.fromScale(-1,1))
#            self.label.setPos(w/2, self.h/2+5)
#        else:
#            self.label.setPos(-w/2, self.h/2+5)

        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemIsSelectable)
        self.setFlip()
        self.setIcon()
        
    def setFlip(self):
        if self.flip:
            self.setTransform(QtGui.QTransform.fromScale(-1, 1))
            self.label.setFlipped()
            for c in self.childItems():
                try:
                    if isinstance(c, Port):
                            c.pinlabel.setFlipped()

                except AttributeError:
                    pass
        else:
            self.setTransform(QtGui.QTransform.fromScale(1, 1))
            self.label.setNormal()
            for c in self.childItems():
                try:
                    if isinstance(c, Port):
                            c.pinlabel.setNormal()

                except AttributeError:
                    pass
        self.setIcon()



    def setIcon(self):
        svgfilepath = os.path.join(respath, 'blocks' , self.icon + '.svg')
        self.img = QtGui.QImage()
        if self.flip:
            self.img.loadFromData(self.create_svg_mirror_txt(svgfilepath))
        else:
            self.img.load(svgfilepath)
        self.update()
                    
    def add_inPort(self, n):
        if isinstance(n, int):
            ypos = -PD*(self.inp-1)/2 + n*PD
            xpos = -(self.w+PW)/2
            name = 'i_pin{}'.format(n)
        else: # tuple (x, y)
            name = n[0]
            xpos = n[1]
            ypos = n[2]
            if xpos > -BWmin/2 - PW/2:
                xpos = -BWmin/2 - PW/2
        port = InPort(self, self.scene, name=name)
        if not isinstance(n, int) and qtpinlabels and len(n) == 3:
            port.pinlabel = textItem(name, anchor=4, parent=port)
            port.pinlabel.setPos(10,0)
        port.block = self
        port.setPos(xpos, ypos)
        return port

    def add_outPort(self, n):
        if isinstance(n, int):
            xpos = (self.w+PW)/2
            ypos = -PD*(self.outp-1)/2 + n*PD
            name = 'o_pin{}'.format(n)
        else: # tuple (x, y)
            name = n[0]
            xpos = n[1]
            ypos = n[2]
            if xpos < BWmin/2 + PW/2:
                xpos = BWmin/2 + PW/2
        port = OutPort(self, self.scene, name=name)
        if not isinstance(n, int) and qtpinlabels and len(n) == 3:
            port.pinlabel = textItem(name, anchor=6, parent=port)
            port.pinlabel.setPos(-10,0)
        port.block = self
        port.setPos(xpos, ypos)
        return port

    def ports(self):
        ports = []
        for thing in self.childItems():
            if isinstance(thing, Port):
                ports.append(thing)
        return ports
        
    def pins(self):
        '''return (inputs, outputs, inouts) that lists of tuples (io, x, y, name)'''
        inputs, outputs, inouts  = [], [], []
        ports = self.ports()
        for p in ports:
            x, y = p.x(), p.y()
            name = p.name
            if isinstance(p, InPort):
                 inputs.append(('i', x, y, name))
            elif isinstance(p, OutPort):
                outputs.append(('o', x, y, name))
            else:
                inouts.append(('io', x, y, name))
        return inputs, outputs, inouts


    def paint(self, painter, option, widget):
        pen = QtGui.QPen()
        pen.setBrush(self.line_color)
        pen.setWidth = LW
        if self.isSelected():
            pen.setStyle(QtCore.Qt.DotLine)
        painter.setPen(pen)
        painter.drawPath(self.path())
        rect = self.img.rect()
        painter.drawImage(-rect.width()/2,-rect.height()/2, self.img)

    def itemChange(self, change, value):
        return value

    def remove(self):
        self.scene.nameList.remove(self.name)
        for thing in self.childItems():
            try:
                thing.remove()
            except:
                pass
        self.scene.removeItem(self)

    def setPos(self, *args):
        if len(args) == 1:
            pt = self.gridPos(args[0])
            super(Block, self).setPos(pt)
        else:
            pt = QtCore.QPointF(args[0],args[1])
            pt = self.gridPos(pt)
            super(Block, self).setPos(pt)
        
    def gridPos(self, pt):
         gr = GRID
         x = gr * ((pt.x() + gr /2) // gr)
         y = gr * ((pt.y() + gr /2) // gr)
         return QtCore.QPointF(x,y)

    def clone(self, pt):
        b = libraries.getBlock(self.blockname,self.libname,scene=self.scene,param=self.parameters,name=self.name)
        b.properties = self.properties
        b.setPos(self.scenePos().__add__(pt))
       
    def save(self, root):
        blk = etree.SubElement(root,'block')
        etree.SubElement(blk,'name').text = self.name
        etree.SubElement(blk,'inp').text = self.inp.__str__()
        etree.SubElement(blk,'outp').text = self.outp.__str__()
        if self.iosetble:
            etree.SubElement(blk,'ioset').text = '1'
        else:
            etree.SubElement(blk,'ioset').text = '0'
        etree.SubElement(blk,'icon').text = self.icon
        etree.SubElement(blk,'parameters').text = self.parameters
        if self.flip:
            etree.SubElement(blk,'flip').text = '1'
        else:
            etree.SubElement(blk,'flip').text = '0'
        etree.SubElement(blk,'posX').text = self.pos().x().__str__()
        etree.SubElement(blk,'posY').text = self.pos().y().__str__()

    def create_svg_mirror_txt(self, svgfilename):
        #generate an svg flie that has text-labels flipped
        dirpath, fname = os.path.split(svgfilename)
#        svgflipped = os.path.join(dirpath, 'flipped', fname)
#        if os.path.exists(svgflipped):
#            return svgflipped
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(svgfilename, parser)
        root = tree.getroot()
        svg_namespace = root.nsmap[None]
        svg_path = '{{{}}}'.format(svg_namespace)
    #    texts = [dom2dict(el) for el in doc.getElementsByTagName('text')]
        texts = root.findall(svg_path+'text')
        for e in texts:
            ff = 'x y text-anchor style'.split()
            rr = []
            for k in ff:
                try:
                    v = e.attrib[k]
                    del e.attrib[k]
                except KeyError:
                    v = '0'
                rr.append(v)
            x, y, anchor, style = rr
            
            

            if style != '0':
                ix = -1
                styleelmnts = style.split(';')
                if 'text-anchor' in style:
                     for ix, se in enumerate(styleelmnts):
                        k, summy, v = se.partition(':')
                        if k == 'text-anchor':
                            anchor = v
                            styleelmnts.pop(ix)
                            break

            if anchor in ['0', 'start'] :
                anchor = 'end'
            elif anchor == 'end':
                anchor = ''

            if anchor:
                if style != '0':
                    styleelmnts.append('text-anchor:'+anchor)
                    e.attrib['style'] = ';'.join(styleelmnts)
                else:
                    e.attrib['text-anchor'] = anchor

            e.attrib['transform'] = 'translate({},{})scale(-1,1)'.format(x, y)

        svgflipped = etree.tostring(root, pretty_print=True)
#        tree.write(svgflipped, pretty_print=True)
        return svgflipped


class textItem(QtWidgets.QGraphicsTextItem):
    '''convenience class, extension of QGraphicsTextItem, that realises aligned text
    textItem.setFlipped() will mirror the text  (in place)
    textItem.setNormal() will put txt in normal (non-mirrored) state
    
    anchor is (look at numpad):
    1: bottom-left
    2: bottom-center
    3: bottom-right
    4: center-left
    5: center-center
    6: center-right
    7: top-left
    8: top-center
    9: top-right'''
    def __init__(self, text, anchor=1, parent=None,comment=False):
        super(textItem, self).__init__(text, parent)
        self.anchor = anchor
        
        # compute dx, dy absed on anchor
        self.dx, self.dy = 0, 0
        if anchor in (4,5,6):
            self.dy = -0.5*self.boundingRect().height()
        elif anchor in (1,2,3):
            self.dy = -self.boundingRect().height()
        
        if anchor in (2,5,8):
            self.dx = -0.5*self.boundingRect().width()
        if anchor in (3,6,9):
            self.dx = -self.boundingRect().width()
            
        self.setNormal()
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemIsSelectable)
#        self.setFlag(self.ItemIgnoresTransformations)
        self.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        self.comment = comment
        self.setAcceptDrops(False)

    def setFlipped(self):
        '''mirror in place (use when parent is flipped'''
        self.setTransform(QtGui.QTransform().translate(self.dx, self.dy).scale(-1,1).translate(-self.boundingRect().width(),0))

    def setNormal(self):
        '''normal orientation'''
        self.setTransform(QtGui.QTransform.fromScale(1,1).translate(self.dx, self.dy))


