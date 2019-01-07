# -*- coding: utf-8 -*-
"""
Created on Thu Dec 13 11:11:59 2018

@author: paul
"""

from libraries.library_math.Bitwise import *
from libraries.library_math.Bitwise import getSymbol as _getSymbol

tooltip = '''Xor function with optional delay'''

properties = {'delay':0.0, 'op':['^', ('^')]} # netlist properties


def getSymbol(param, properties,parent=None,scene=None):
    pp = dict(_name=name, _libname=libname)
    pp.update(properties)
    return _getSymbol(param, pp,parent,scene)
