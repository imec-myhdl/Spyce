import os
import supsisim.block 
from supsisim.const import viewEditors
from supsisim.dialg import error

def getBlock(blockname,libname,parent=None,scene=None, param=dict(), name=None):
    try:
        exec('import libraries.library_' + libname + '.' + blockname)
    except:
        error('Symbol not found')
        return False
    reload(eval('libraries.library_' + libname + '.' + blockname))
    try:
        if not param:
            param = eval('libraries.library_{}.{}.parameters'.format(libname,blockname))
        func = eval('libraries.library_{}.{}.getSymbol'.format(libname,blockname))
        b = func(param,parent,scene)
        if isinstance(b,supsisim.block.Block):
            if name:
                b.name = name
                b.label.setPlainText(name)
            return b
        else:
            error('getSymbol returned no block')
            return False
    except Exception as e:
#        import sys
#        exc_type, exc_obj, exc_tb = sys.exc_info()
#        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#        print(exc_type, fname, exc_tb.tb_lineno,e)
        options = ('parameters','properties')
        for o in options:
            exec(o + ' = libraries.library_' + libname + '.' + blockname + '.' + o)
        attributes = dict()
        if name:
            attributes['name'] = name
        else:
            attributes['name'] = blockname
        attributes['libname'] = libname
        attributes['input'] = eval('libraries.library_' + libname + '.' + blockname + '.inp')
        attributes['output'] = eval('libraries.library_' + libname + '.' + blockname + '.outp')
        attributes['icon'] = eval('libraries.library_' + libname + '.' + blockname + '.iconSource')
        try:
            attributes['height'] = eval('libraries.library_' + libname + '.' + blockname + '.height')
        except:
            pass
#        if 'inp' in param.keys():
#            attributes['input'] = param['inp']
#        if 'outp' in param.keys():
#            attributes['output'] = param['outp']
        return supsisim.block.Block(attributes,parameters,properties,blockname,libname,parent,scene)

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
                    if type == 'diagram':
                        block = False
                    for viewEditor in viewEditors:
                        if type == viewEditor['type']:
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