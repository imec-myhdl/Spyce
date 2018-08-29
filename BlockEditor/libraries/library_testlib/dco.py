name = 'dco' #zelfde als bestand naam 
libname = 'testlib' #zelfde als map naam

inp = [('i_pvt', -150, -60), ('i_acq', -150, -20), ('i_trk', -150, 20), ('i_mod', -150, 60)]
outp = [('o_lop', 150, -60), ('o_lon', 150, -20)]

parameters = dict(inp=[('i_pvt', -150, -60), ('i_acq', -150, -20), ('i_trk', -150, 20), ('i_mod', -150, 60)],outp=[('o_lop', 150, -60), ('o_lon', 150, -20)])
properties = {} #voor netlisten
#view variables:
iconSource = 'dco'
textSource = 'libraries/library_testlib/dco.py'



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