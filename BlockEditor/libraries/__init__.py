import os
import supsisim.block 
from supsisim.const import viewEditors
from supsisim.dialg import error




blocks = dict()


def getBlock(blockname,libname,parent=None,scene=None, param=dict(), name=None):
    source     = 'libraries.library_{}.{}'.format(libname, blockname)
    try:
        exec('import ' + source)
    except Exception as e:
        raise e
        error('error in {}.py, message is '.format(source, str(e)))
        return False
    reload(eval('libraries.library_' + libname + '.' + blockname)) # make sure we reload the module
    blk = None    
    exec('from libraries.library_{} import {} as blk'.format(libname, blockname))
    blocks[libname+'/'+blockname] = blk
    blk.name    = blockname
    blk.libname = libname
    blk.textSource = os.path.join('library_'+libname,  blockname+'.py')
    if not 'iconSource' in blk.__dict__:
        blk.iconSource = None
    blk.views['textSource'] = blk.textSource

    if not param:
        param = blk.parameters # use defaults
    try:
        b = blk.getSymbol(param, parent, scene)
        if isinstance(b,supsisim.block.Block):
            if name:
                b.name = name
                b.label.setPlainText(name)
            return b
        else:
            error('getSymbol returned no block')
            return False
    except Exception as e:
        parameters = blk.parameters
        properties = blk.properties
        attributes = dict()
        attributes['name']    = name if name else blockname
        attributes['libname'] = libname
        attributes['input']   = blk.inp
        attributes['output']  = blk.outp
        attributes['icon']    = blk.iconSource
#        try:
#           attributes['height'] = bb.height
#        except:
#            pass
        return supsisim.block.Block(attributes,parameters,properties,blockname,libname,parent,scene)

def getViews(blockname,libname):
    return blocks[libname+'/'+blockname].views
    
def readLibrary(libname):
    files = os.listdir('libraries/' + libname)
    blocks = set()
    for blockname in files:
        if blockname.startswith('__init__'):
            continue
        if not blockname.lower().endswith('.py'):
            continue
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
            blockname = blockname.rpartition('.')[0]
            blocks.add(blockname)
            
    return blocks


libs = dict()

libroot = os.path.dirname(__file__)

for libname in os.listdir(libroot):
    if libname.startswith('library_'):
        libs[libname.replace('library_','')] = readLibrary(libname)
        
        
default = 'common'