# -*- coding: utf-8 -*-
"""
Created on Thu Dec 13 11:11:59 2018

@author: paul
"""

from libraries.library_math.Bitwise import *
from libraries.library_math.Bitwise import getSymbol as _getSymbol

tooltip = '''And function with optional delay
     e.g. a0 | a1
the output can be inverted by putting Z parameter to '-' 
the inputs can be inverted by putting A parameter to '-' 
(uses Bitwise block as primitive)'''

properties = {'delay':0.0, 'op':['|', ('|')]} # netlist properties


def getSymbol(param, properties,parent=None,scene=None):
    pp = dict(_name=name, _libname=libname)
    pp.update(properties)
    return _getSymbol(param, pp,parent,scene)
