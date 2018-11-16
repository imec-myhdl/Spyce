# cell definition
# name = 'socket'
# libname = 'Socket'

inp = 1
outp = 0

parameters = dict(inp=1,outp=0)
properties = {'name': 'unixsocketCBlk', 'Socket': " 'bsock'"} #voor netlisten
#view variables:
iconSource = 'SOCK'



import supsisim.block 

def getSymbol(param, properties,parent=None,scene=None,):
    attributes = dict()
    attributes['name'] = name
    attributes['libname'] = libname
    attributes['input'] = param['inp'] if 'inp' in param else inp
    attributes['output'] = param['outp'] if 'outp' in param else outp
    attributes['icon'] = iconSource
    
    
    return supsisim.block.Block(attributes,param,properties,name,libname,parent,scene)
    

views = {'icon':iconSource}
