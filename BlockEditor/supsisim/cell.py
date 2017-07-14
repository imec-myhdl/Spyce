# -*- coding: utf-8 -*-
"""
Created on Fri Jun  9 13:04:51 2017

@author: paul
"""
from block import Block

class Cell(Block):
    '''Cell master object: template for a cell definition. 
    An instantiation is in fact a Block instance (== symbol)
    
    schematic() returns an empty list of components. Should be overloaded for cells that contains sub-hierarchy
    netlist(mode=None) ...
    edit()
    '''
    
    default_parameters = 'inp outp icon params iosetble'    
    
    def __init__(self, **kwargs):
        self.cellname   = self.__class__.__name__
        self.inp        = []
        self.outp       = []
        self.icon       = ''
        self.params     = ''
        self.iosetble   = False
        self.components = [] # holds the schematic components (Cell)
        self._symbol    = None 
        self._x          = 0
        self._y          = 0
        self._flip       = False
        self.__dict__.update(kwargs)

    @property
    def x(self):
        if self._symbol:
            return self._symbol.x()
        return self._x
    
    @x.setter
    def x(self,value):
        if self._symbol:
            self._symbol.setX(value)
        else:
            self._x = value

    @property
    def y(self):
        if self._symbol:
            return self._symbol.x()
        return self._x
    
    @y.setter
    def y(self,value):
        if self._symbol:
            self._symbol.setY(value)
        else:
            self._y = value
        
    @property
    def flip(self):
        if self._symbol:
            return self._symbol.flip
        return self._flip
    
    @flip.setter
    def flip(self,value):
        if self._symbol:
            self._symbol.flip=value
        else:
            self._flip = value

        
    def symbol(self, scene, x=None, y=None, flip=False):
        '''returns a Block instance'''
        self._symbol = Block(None, scene, name=self.cellname)
        if x !=None :
            self.x = x
        if y !=None :
            self.y = y
        self.flip = flip
        self._symbol.inp      = len(self.inp)
        self._symbol.outp     = len(self.outp)
        self._symbol.icon     = self.icon
        self._symbol.params   = self.params
        self._symbol.iosetble = self.iosetble
        return self._symbol
        
    def schematic(self, scene):
        ''''generate the schematic'''
        for item in self.components:
            item.symbol(scene) # add to scene
            
    def add(self, component, x=0, y=0, flip=False):
        self.components.append(component)
        component.x = x
        component.y = y
        component.flip = flip
        
    def __str__(self):
        fmt = '{cellname}({args})'
        args = []
        for k in Cell.default_parameters.split():
            v = self.__dict__[k]
            if v:
                args.append('{}={}'.format(k, repr(v)))
        if self.x:
            args.append('x={}'.format(self.x))
        if self.y:
            args.append('y={}'.format(self.y))
        if self.flip:
            args.append('flip=True')
                
        return fmt.format(cellname=self.cellname, args=', '.join(args))
        
    def save(self):
        ''''returns a string that should be correct python syntax'''
        fmt = \
'''
# automatically generated, do not edit

from cell import Cell

class {cellname}(Cell):
    def __init__(self, **kwargs):
        super({cellname}, self).__init__(**kwargs)
        
'''
        celltxt = fmt.format(cellname=self.cellname)
        
        sch = []
        for component in self.components:
            sch.append('        self.add('+str(component)+')')
        
        if sch:
            celltxt += '    def schematic(self):\n'
            celltxt += '\n'.join(sch) + '\n'
        
        return celltxt


class testcell(Cell):
    def __init__(self, **kwargs):
        super(testcell, self).__init__(**kwargs)
        

effe = testcell()

effe.add(testcell(inp=3), x=1, y=2, flip=True)

print effe.save()
