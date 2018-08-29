name = 'test1' #zelfde als bestand naam 
libname = 'testlib' #zelfde als map naam

inp = [('a', -40, -20), ('b', -40, 20)]
outp = [('z', 40, 0)]

parameters = dict(inp=[('a', -40, -20), ('b', -40, 20)],outp=[('z', 40, 0)])
properties = {'name': 'sumBlk', 'Gains': ' [1,-1]'} #voor netlisten
#view variables:
iconSource = 'test1'
textSource = 'libraries/library_testlib/test1.py'



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