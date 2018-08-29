name = 'dtc_delay' #zelfde als bestand naam 
libname = 'testlib' #zelfde als map naam

inp = [('i_a', -150, -60), ('i_row', -150, -20), ('i_col', -150, 20), ('i_res_tune', -150, 60)]
outp = [('o_zn', 150, -60)]

parameters = dict(inp=[('i_a', -150, -60), ('i_row', -150, -20), ('i_col', -150, 20), ('i_res_tune', -150, 60)],outp=[('o_zn', 150, -60)])
properties = {} #voor netlisten
#view variables:
iconSource = 'dtc_delay'
textSource = 'libraries/library_testlib/dtc_delay.py'



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