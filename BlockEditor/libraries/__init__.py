# -*- coding: utf-8 -*-
"""
#==============================================================================
# libaries initialisation
#==============================================================================



"""
import os

from supsisim.const import viewTypes
#from supsisim.dialg import error

libs = dict()  # key = library name (minus the 'library_' prefix)
#                value = a set containing all blocknames

libroot = os.path.dirname(__file__) # home of all libaries
libprefix = 'library_'


def libpath(libname, root=libroot):
    '''return full path of libary libname'''
    if libname.startswith(libprefix):
        return os.path.join(root, libname)
    else:
        return os.path.join(root, libprefix + libname)

def blockpath(libname, blockname):
    '''return full path of libary libname'''
    return os.path.join(libpath(libname), blockname+'.py')
    
def moduleName(libname, blockname):
    return '{}.{}.{}'.format(os.path.basename(libroot), libprefix+libname, blockname)

def readLibraries():
    dirs = next(os.walk(libroot))[1]
    for dirname in dirs:
        if dirname.startswith(libprefix):
            libname = dirname[len(libprefix):]
            libs[libname] = readLibrary(libname)
    
def readLibrary(libname):
    files = next(os.walk(libpath(libname)))[2]
    blocks = set()
    for blockname in files:
        if not blockname.endswith('.py'): # only python files
            continue
        if blockname.startswith('__init__'): # skip __init__
            continue
        for  viewtype, (editor, extension) in viewTypes.items():
            if blockname.endswith(extension):
                if viewtype == 'python':
                    blockname = blockname[:-len(extension)]
                    blocks.add(blockname)
                else: # other python type (e.g. diagram/myhdl)
                    break 
    return blocks

def rmBlock(libname, blockname):
    '''remove a block from library administration (and disk)'''
    # remove self (if not yet removed)
    fp = blockpath(libname, blockname)
    if os.path.isfile(fp):
        os.remove(fp)
    # update libary administration
    libs[libname].remove(blockname)
        
readLibraries()
default = 'common'