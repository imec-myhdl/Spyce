# -*- coding: utf-8 -*-
"""
#==============================================================================
# block module
#==============================================================================

getBlockModule
    read the python module of block from disk
    returns module
    
getBlock
    create a Block object (to be used in the graphical environment)

rmBlock
    removes a Block from disk

saveBlock
    save a (new) block to disk (as python module
    returns src
    
Block
    class definition for the Block object
"""
# aim for python 2/3 compatibility

from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

from  Qt import QtGui, QtWidgets, QtCore # see https://github.com/mottosso/Qt.py

import os
import subprocess
from copy import copy
from collections import OrderedDict

import libraries
from supsisim.port  import Port, isPort
from supsisim.const import GRID, PW, LW, BWmin, BHmin, PD, respath, \
                            celltemplate, colors, viewTypes
from supsisim.dialg import error
from supsisim.text  import textItem
from supsisim.src_import import import_module_from_source_file

from supsisim.svg_utils import svg2png #createSvgMirrorTxt

block_modules = dict()

#==============================================================================
# block module functions deal with the imported python module (block definition)
#==============================================================================
def _addBlockModuleDefaults(libname, blockname):
    '''add default settings to a loaded block_module'''
    blk = block_modules[libname+'/'+blockname]
    blk.name    = blockname
    blk.libname = libname
    blk.textSource = libraries.blockpath(libname, blockname)
    try:
        if not 'icon' in blk.views:
            blk.views['icon'] = None
        if not hasattr(blk, 'bbox'):
            blk.bbox = None
        for pp in ['properties', 'parameters']:
            if not hasattr(blk, pp):
                setattr(blk, pp, dict())
    except Exception as e:
        raise Exception('Block {}.{} raised error {}'.format(libname,blockname, str(e)) )

    p = libraries.libpath(libname)
    for viewname, (ed, ext) in viewTypes.items():
        fn = os.path.join(p, blockname + ext)
        if os.path.isfile(fn):
            blk.views[viewname] = fn        

def getBlockModule(libname, blockname):
    '''read python module of block from disk'''
    fpath = libraries.blockpath(libname, blockname)
    blk = import_module_from_source_file(fpath)
    block_modules[libname+'/'+blockname] = blk
    _addBlockModuleDefaults(libname, blockname)
    return blk

#==============================================================================
# snap to grid
#==============================================================================
def gridPos(pt):
     gr = GRID
     x = gr * ((pt.x() + gr /2) // gr)
     y = gr * ((pt.y() + gr /2) // gr)
     return QtCore.QPointF(x,y)
    
#==============================================================================
# helper function to easily create a Block object        
#==============================================================================
def getBlock(libname, blockname, parent=None, scene=None, param=dict(), properties=dict(), name=None, flip=False):
    '''create a Block'''
    blk = getBlockModule(libname, blockname)
    if blk.parameters and not param:
        param = blk.parameters
    if blk.properties and not properties:
        properties = blk.properties

    try:
         b = blk.getSymbol(param, properties, parent, scene)
    except AttributeError:
         b = None
    if b: # pcell
        b.libname = libname
        
        if isinstance(b, Block):
            if name:
                if scene:
                    scene.rmBlkName(b)
                    b.name = name
                    scene.addBlkName(b)
                else:
                    b.name = name

                b.label.setText(name)
                b.flip = flip
                b.setFlip()
            if hasattr(blk,'tooltip'):
                b.setToolTip(blk.tooltip)
            return b
        else:
            error('getSymbol returned no block')
        return False
#        except Exception as e:
#            error('libary_{}/{}.py contains error:\n{}'.format(libname, blockname, str(e)))
#            return False

    else: # std block
        if param:
            error('pcell {}.{}.getSymbol did not return block'.format(libname, blockname))
        else:
            parameters = blk.parameters
            properties = blk.properties
            attributes = dict()
            attributes['name']    = name if name else blockname
            attributes['libname'] = libname
            attributes['input']   = blk.inp
            attributes['output']  = blk.outp
            attributes['icon']    = blk.views['icon']
            attributes['bbox']    = blk.bbox
            attributes['flip']    = flip
            b =  Block(attributes,parameters,properties,blockname,libname,parent,scene)
            if hasattr(blk,'tooltip'):
                b.setToolTip(blk.tooltip)
            return b

def getViews(libname, blockname):
    '''return the views that are defined for this block
    if viewType is specified, return the value if present'''
    return getBlockModule(libname, blockname).views

    
#==============================================================================
# helper function to easily remove a Block   
#==============================================================================
def rmBlock(libname, blockname):
    # first remove views (one of them is the file itself)
    blk = block_modules[libname + '/'+ blockname]
    for type, filename in blk.views.items():
        if filename:
            fn1 = os.path.join(libraries.libpath(libname), filename)
            fn2 = os.path.join(os.getcwd(), filename)
            if os.path.isfile(fn1):
                os.remove(fn1)
            elif os.path.isfile(fn2):
                os.remove(fn2)
            elif os.path.isfile(filename):
                os.remove(filename)
    libraries.rmBlock(libname, blockname)
        
#==============================================================================
# helper function to easily save a (new) Block   
#==============================================================================
def saveBlock(libname, blockname, pins, icon=None, bbox=None, properties=dict(), parameters=dict()):
    '''if library is set, save a (new) block to disk (as python module)
    returns src'''
    
    inp, outp, io = pins
    
    # optionals
    views = dict()
    views['icon'] = icon
    
    bbox = 'bbox = {}\n'.format(str(bbox)) if bbox else None
    src = celltemplate.format(name=blockname,
                            libname=libname,
                            inp=inp,
                            outp=outp,
                            io=io,
                            bbox=bbox,
                            properties=properties,
                            parameters=parameters,
                            views=views)
    if libname:
        fname = os.path.join(libraries.libroot, libraries.libprefix+libname, blockname+'.py')
        with open(fname, 'wb') as f:
            f.write(src)
        libraries.libs[libname].add(blockname)
        getBlockModule(libname, blockname)
        return src

#==============================================================================
# helper function to calculate the bounding box, based on pins
#==============================================================================
def calcBboxFromPins(inp, outp, io=[]):
    if isinstance(inp, int):
        Ni = inp  if isinstance(inp, int) else len(inp)
        No = outp if isinstance(outp, int) else len(outp)
        Nports = max(Ni, No)
        w = BWmin
        h = max(Nports*PD, BHmin)
        left = -w/2
        top = -h/2
    else:
        # find bounding box
        x0, y0, x1, y1 = None, None, None, None
        for item in inp + outp + io:
            x0 = item[1] if x0 == None else min(x0, item[1])
            x1 = item[1] if x1 == None else max(x1, item[1])
            y0 = item[2] if y0 == None else min(y0, item[2])
            y1 = item[2] if y1 == None else max(y1, item[2])
            #print(y0,y1,y,self.name)
        if x0 != None and x1 != None:
            left = x0
            w = max(x1 - x0, BWmin)
        else:
            w = BWmin
            left = -w/2
            
            
        if y0 != None and y1 != None:
            top = y0 - PD/2
            h = max(y1 - y0 + PD, BHmin)
        else:
            h = BHmin
            top = - h/2
    return (left, top, w, h)        
#==============================================================================
# main Block class
#==============================================================================
class Block(QtWidgets.QGraphicsPathItem):
    """A block holds ports that can be connected to."""
    def __init__(self,attributes, parameters, properties, blockname, libname, parent=None, scene=None):
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
        try:
            self.name = self.scene.addBlkName(self)
        except AttributeError:
            pass   
        self.inp = attributes.pop('input')
        self.outp = attributes.pop('output')
        self.icon = attributes.pop('icon') if 'icon' in attributes else None
           
        self.flip = attributes.pop('flip') if 'flip' in attributes else False
        self.type = attributes.pop('type') if 'type' in attributes else 'Block'
        self.libname = attributes.pop('libname')
        self.bbox = attributes.pop('bbox') if 'bbox' in attributes else None
        
        self.parameters = parameters
        self.properties = properties
        
        self.label = None
        
        self.png = None
        self.pngmirr = None
        
        self.linecolor = colors['block']

        if self.scene:
            self.setup()
    
#    def __str__(self):
#        txt  = 'Name         :' + self.name.__str__() +'\n'
#        txt += 'Input ports  :' + self.inp.__str__() + '\n'
#        txt += 'Output ports :' + self.outp.__str__() + '\n'
#        txt += 'Icon         :' + self.icon.__str__() + '\n'
#        txt += 'Properties       :' + self.properties.__str__() + '\n'
#        for thing in self.childItems():
#            print(thing)
#        return txt
        
#    def __repr__(self):
#        return str(self.toData())


    def add_Port(self, n, tp='input', spacing=PD):
        if isinstance(n, int):
            if tp == 'input':
                xpos = -(self.w)/2
                ypos = -spacing*(self.inp-1)/2 + n*spacing
                name = '.i_{}'.format(n) # . makes it hidden
                if xpos > -BWmin/2:
                    xpos = -BWmin/2
            elif tp == 'output':
                xpos = (self.w)/2
                ypos = -spacing*(self.outp-1)/2 + n*spacing
                name = '.o_{}'.format(n) # . makes it hidden
                if xpos < BWmin/2 :
                    xpos = BWmin/2 
          
        else: # tuple (name, x, y)
            name = n[0]
            xpos = n[1]
            ypos = n[2]
            if tp == 'input':
                if xpos > -BWmin/2:
                    xpos = -BWmin/2
            elif tp == 'output':
                 if xpos < BWmin/2 :
                    xpos = BWmin/2 
                   
        port = Port(self, self.scene, label=name, porttype=tp)
        port.block = self
        port.setPos(QtCore.QPoint(xpos, ypos) - self.center)
        return port


    def calcBboxFromPins(self):
        return calcBboxFromPins(self.inp, self.outp)
        
    def clone(self, pt):
        b = getBlock(self.libname, self.blockname, scene=self.scene, \
                     param=self.parameters, name=self.name)
        b.properties = self.properties
        b.setPos(self.scenePos().__add__(pt))
        return b
        
    def addView(self, viewtype, fname):
        if viewtype not in viewTypes:
            error('viewtype {} is not defined in const.py'.format(viewtype))
            return
        views = self.getViews()
        if viewtype in views:
            error('viewtype {} is already present'.format(viewtype))
            return
        views[viewtype] = fname
        self.updateOnDisk(views)

    def getViews(self):
        '''return the views that are defined for this block
        if viewType is specified, return the value if present'''
        return getViews(self.libname, self.blockname)

    def gridPos(self, pt):
         gr = GRID
         x = gr * ((pt.x() + gr /2) // gr)
         y = gr * ((pt.y() + gr /2) // gr)
         return QtCore.QPointF(x,y)


    def paint(self, painter, option, widget):
        pen = QtGui.QPen(self.linecolor)
        pen.setWidth = LW
        if self.isSelected():
            pen.setStyle(QtCore.Qt.DotLine)
        painter.setPen(pen)
        painter.drawPath(self.path())
        rect = self.img.rect()
        painter.drawImage(-rect.width()/2,-rect.height()/2, self.img)

        
#    def pins(self):
#        '''return (inputs, outputs, inouts) that lists of tuples (io, x, y, name)'''
#        inputs, outputs, inouts  = [], [], []
#        ports = self.ports()
#        for p in ports:
#            x, y = int(p.x() + self.center.x()) , int(p.y() + self.center.y())
#            name = p.name
#            if isinstance(p, InPort):
#                 inputs.append(('i', x, y, name))
#            elif isinstance(p, OutPort):
#                outputs.append(('o', x, y, name))
#            else:
#                inouts.append(('io', x, y, name))
#        return inputs, outputs, inouts

    def ports(self, retDict=False):
        if retDict:
            ports = dict()
            for item in self.childItems():
                if isinstance(item, Port):
                    ports[item.label.text()] = item
        else:
            ports = []
            for item in self.childItems():
                if isinstance(item, Port):
                    ports.append(item)
        return ports

                     
    def remove(self):
        self.scene.rmBlkName(self)
        for thing in self.childItems():
            try:
                thing.remove()
            except:
                pass
        self.scene.removeItem(self)

    def rmView(self, viewname):
        '''add a view and update disk'''
        dd = self.getViews.copy()
        if 'textSource' in dd:
            del dd['textSource']
        if viewname in dd:
            del dd[viewname]
        self.updateOnDisk(dd)

    def setFlip(self, flip=None):
        if flip: 
            self.flip = flip
        if self.flip:
            self.setTransform(QtGui.QTransform.fromScale(-1, 1))
            self.label.setFlipped()
        else:
            self.setTransform(QtGui.QTransform.fromScale(1, 1))
            self.label.setNormal()
        for p in self.ports():
            p.setFlip()
        self.setIcon()


    def setIcon(self, iconpath=None):
        self.img = QtGui.QImage()
        if iconpath:
            self.icon = iconpath
        if self.icon is None: # not set
            return
        elif self.icon.lower().endswith('.svg'): # new style (path from libroot)
            svgfilepath = self.icon
            # make relative to the directory of the block
            if not os.path.isabs(svgfilepath):
                svgfilepath = os.path.join(libraries.libpath(self.libname), svgfilepath)
        else: # old style
            svgfilepath = os.path.join(respath, 'blocks' , self.icon + '.svg')

        self.icon = svgfilepath
#==============================================================================
#         hack png 
#==============================================================================
        ret = svg2png(svgfilepath)
        if ret:
            self.png, self.pngmirr = ret 
        
        if self.flip and self.pngmirr and os.path.isfile(self.pngmirr):
            self.img.load(self.pngmirr)
        elif self.png and os.path.isfile(self.png):
            self.img.load(self.png)
        
            self.update()

    def setPos(self, *args):
        delta = QtCore.QPointF(0,0)
        if self.bbox:
            left, top, w, h = self.bbox
            mid = QtCore.QPointF(w/2, h/2)
            delta = mid - self.gridPos(mid)
        if len(args) == 1:
            pt = self.gridPos(args[0])
            super(Block, self).setPos(pt-delta)
        else:
            pt = QtCore.QPointF(args[0],args[1])
            pt = self.gridPos(pt)
            super(Block, self).setPos(pt-delta)
    
        

    def setLabel(self):
        name = self.name
        if self.label:
            self.label.setText(name)
        else:
            self.label = textItem(name, anchor=8, parent=self)
            self.label.setText(name)
        self.label.setPos(0, self.h/2)
        self.setFlip()
 
       
    def setup(self):
        self.setIcon()
        self.ports_in = []
        bbox = self.bbox if self.bbox else calcBboxFromPins(self.inp, self.outp)
#        print (self.name, bbox)
        left, top, self.w, self.h = bbox
        self.center = QtCore.QPoint(int(left+self.w/2), int(top+self.h/2))
        p = QtGui.QPainterPath()
        p.addRect(-self.w/2 + PW/2, -self.h/2, self.w - PW, self.h)

        self.setPath(p)
        
        if isinstance(self.inp, int):
            spacing = 2*PD if self.inp <= 2 else PD
            for n in range(0,self.inp): # legacy: self.inp is integer number
                self.add_Port(n, 'input', spacing)
        else:
            for n in self.inp: # new: self.inp is list of tuples (name, x,y)
                self.add_Port(n, 'input')

        if isinstance(self.outp, int):
            spacing = 2*PD if self.inp <= 2 else PD
            for n in range(0,self.outp):# legacy: self.out = integer number
                self.add_Port(n, 'output', spacing)
        else:
            for n in self.outp: # new: self.outp is list of tuples (name, x,y)
                self.add_Port(n, 'output')

        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemIsSelectable)
        self.setLabel()

    def setView(self, viewname, viewvalue):
        '''add a view and update disk'''
        views = copy(self.getViews())
        if 'textSource' in views:
            del views['textSource']
        views[viewname] = viewvalue
        self.updateOnDisk(dd=dict(views=views))

    def toData(self):
        data = OrderedDict(type='block')
        
        data['blockname'] = self.blockname
        data['libname'] = self.libname
        data['x'] = self.x()
        data['y'] = self.y()
        
        # optional fields
        if self.flip:
            data['flip'] = self.flip
        if self.label:
            data['label'] = self.label.toData()
        if self.properties:
            data['properties'] = self.properties

        # pcell
        if self.parameters:
            data['parameters'] = self.parameters 

        return data

    def fromData(self,data):
#        self = getBlock(data['libname'], data['blockname'], scene=self,\
#            param=data['parameters'])
        self.setPos(data['x'],data['y'])
        if 'label' in data:
            self.label.fromData(data['label'])
        if 'properties' in data:
            self.properties = data['properties']
        else:
            self.properties = dict()
        if 'flip' in data:
            self.setFlip(data['flip'])

        
    
    def updateOnDisk(self, dd=dict(), writeback=True):
        '''replace assignments with new values for variable names in dd
        and write back to disk'''
        fname = libraries.blockpath(self.libname, self.blockname)
        src = []
        with open(fname) as f:
            lines = f.readlines()
            ix = 0
            while ix < len(lines):
                line = lines[ix]
                s = line.replace('=', ' = ').split()
                if len(s) > 2  and line.startswith(s[0]) and  s[0] in dd and s[1] == '=':
                    # assignment without leading whitespace
                    key = s[0]
                    while line.endswith('\\\n') or line.strip().endswith(','):
                        ix += 1
                        line = lines[ix]
                    # get comment if present
                    line, _ , cmt = line.partition('#')
                    if cmt:
                        cmt = ' # '+ cmt.strip()
                    line = '{} = {}\n'.format(key, dd[key], cmt)
                
                src.append(line)
                ix += 1

        src = ''.join(src)
        if writeback:
            with open(fname, 'wb') as f:
                f.write(src)
                
        getBlockModule(self.libname, self.blockname) # update module
        return src

    
    
            
        
                    




        
       
#    def save(self, root):
#        blk = etree.SubElement(root,'block')
#        etree.SubElement(blk,'name').text = self.name
#        etree.SubElement(blk,'inp').text = self.inp.__str__()
#        etree.SubElement(blk,'outp').text = self.outp.__str__()
#        if self.iosetble:
#            etree.SubElement(blk,'ioset').text = '1'
#        else:
#            etree.SubElement(blk,'ioset').text = '0'
#        etree.SubElement(blk,'icon').text = self.icon
#        etree.SubElement(blk,'parameters').text = self.parameters
#        if self.flip:self
#            etree.SubElement(blk,'flip').text = '1'
#        else:
#            etree.SubElement(blk,'flip').text = '0'
#        etree.SubElement(blk,'posX').text = self.pos().x().__str__()
#        etree.SubElement(blk,'posY').text = self.pos().y().__str__()


def isBlock(item):
    return isinstance(item, Block)
