name = 'Socket' #zelfde als bestand naam 
libname = 'Socket' #zelfde als map naam

inp = 0
outp = 1

parameters = dict(inp=0,outp=1)
properties = {'name': 'unixsocketSBlk', 'Default outputs': '[0.]', 'Socket': " 'ssock'"} #voor netlisten
#view variables:
iconSource = 'SOCK'
textSource = 'libraries/library_Socket/Socket.py'



import supsisim.block 

def getSymbol(param,parent=None,scene=None,):
    attributes = dict()
    attributes['name'] = name
    attributes['libname'] = libname
    attributes['input'] = param['inp'] if 'inp' in param else inp
    attributes['output'] = param['outp'] if 'outp' in param else outp
    attributes['icon'] = iconSource
    
    
    return supsisim.block.Block(attributes,param,properties,name,libname,parent,scene)
    

views = {'icon':iconSource,'text':textSource}