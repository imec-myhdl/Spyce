import os
from supsisim.block import Block
from supsisim.const import viewEditors

def getBlock(blockname,libname,parent=None,scene=None, param=dict(), test=False, name=None):
    exec('import libraries.library_' + libname + '.' + blockname)
    reload(eval('libraries.library_' + libname + '.' + blockname))
    options = ('parameters','properties')
    for o in options:
        exec(o + ' = libraries.library_' + libname + '.' + blockname + '.' + o)
    attributes = dict()
    attributes['name'] = blockname
    attributes['libname'] = libname
    attributes['input'] = eval('libraries.library_' + libname + '.' + blockname + '.inp')
    attributes['output'] = eval('libraries.library_' + libname + '.' + blockname + '.outp')
    attributes['icon'] = eval('libraries.library_' + libname + '.' + blockname + '.iconSource')
    
    if 'inp' in param.keys():
        attributes['input'] = param['inp']
    if 'outp' in param.keys():
        attributes['output'] = param['outp']
    return Block(attributes,parameters,properties,blockname,libname,parent,scene)

def getViews(blockname,libname):
    exec('import libraries.library_' + libname + '.' + blockname)
    reload(eval('libraries.library_' + libname + '.' + blockname))
    views = eval('libraries.library_' + libname + '.' + blockname + '.views')
    return views
    
def readLibrary(libname):
    files = os.listdir('libraries/' + libname)
    blocks = set()
    for blockname in files:
        if not blockname.startswith('__init__'):
            block = True
            if '_' in blockname:
                ending = blockname.split('_')[-1]
                if '.' in ending:
                    type = ending.split('.')[0]
                    if type in viewEditors.keys() or type == 'diagram':
                        block = False
            if block:
                blockname = blockname.replace('.pyc','')
                blockname = blockname.replace('.py','')
                blocks.add(blockname)
            
    return blocks

files = os.listdir('libraries')

libs = dict()

for libname in files:
    if libname.startswith('library_'):
        libs[libname.replace('library_','')] = readLibrary(libname)
        
        
default = 'common'