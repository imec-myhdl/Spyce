import os
from supsisim.block import Block

def getBlock(blockname,libname,parent=None,scene=None, param=dict(), test=False):
    exec('import libraries.library_' + libname + '.block_' + blockname)
    reload(eval('libraries.library_' + libname + '.block_' + blockname))
    options = ('attributes','parameters','properties','views')
    for o in options:
        exec(o + ' = libraries.library_' + libname + '.block_' + blockname + '.' + o)
    attributes = dict(attributes)
    attributes['libname'] = libname
    if 'inp' in param.keys():
        attributes['input'] = param['inp']
    if 'outp' in param.keys():
        attributes['output'] = param['outp']
    return Block(attributes,parameters,properties,views,blockname,libname,parent,scene)

def readLibrary(libname):
    files = os.listdir('libraries/' + libname)
    blocks = set()
    for blockname in files:
        if blockname.startswith('block_'):
            blockname = blockname.replace('.pyc','')
            blockname = blockname.replace('.py','')
            blocks.add(blockname.replace('block_',''))
            
    return blocks

files = os.listdir('libraries')

libs = dict()

for libname in files:
    if libname.startswith('library_'):
        libs[libname.replace('library_','')] = readLibrary(libname)
        
        
default = 'common'