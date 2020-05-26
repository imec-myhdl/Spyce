# cell definition
# name = 'Generic_C_Block'
# libname = 'nonlin'

inp = 1
outp = 1

parameters = dict(inp=1,outp=1)
properties = {'String': " ''", 'States': ' [0,0]', ' Int pars': '[]', 'Real pars': ' []', ' Function name': " 'test'", 'FeedForw': ' 0', 'name': 'genericBlk'} #voor netlisten
#view variables:
iconSource = 'CBLOCK'



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
