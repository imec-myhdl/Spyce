# cell definition
# name = 'FMU'
# libname = 'nonlin'

inp = 1
outp = 1

parameters = dict(inp=1,outp=1)
properties = {'Major step': ' 0.01', 'Feedthrough': ' 0', 'OUT_REF': " ['y']", 'IN_REF': " ['u']", 'FMU_NAME': " ''", 'name': 'FmuBlk'} #voor netlisten
#view variables:
iconSource = 'FMU'



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
