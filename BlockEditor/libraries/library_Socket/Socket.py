# cell definition
# name = 'Socket'
# libname = 'Socket'

inp = 0
outp = 1

parameters = dict(inp=0,outp=1)
properties = {'name': 'unixsocketSBlk', 'Default outputs': '[0.]', 'Socket': " 'ssock'"} #voor netlisten
#view variables:
iconSource = 'SOCK'



import spycelib.block 

def getSymbol(param, properties,parent=None,scene=None,):
    attributes = dict()
    attributes['name'] = name
    attributes['libname'] = libname
    attributes['input'] = param['inp'] if 'inp' in param else inp
    attributes['output'] = param['outp'] if 'outp' in param else outp
    attributes['icon'] = iconSource
    
    
    return spycelib.block.Block(attributes,param,properties,name,libname,parent,scene)
    

views = {'icon':iconSource}
