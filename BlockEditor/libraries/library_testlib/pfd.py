name = 'pfd' #zelfde als bestand naam 
libname = 'testlib' #zelfde als map naam

inp = [('i_ref', -150, -60), ('i_fb', -150, -20), ('i_rstref_n', -150, 20), ('i_rstfb_n', -150, 60)]
outp = [('o_upn', 150, -60), ('o_dnn', 150, -20)]

parameters = dict(inp=[('i_ref', -150, -60), ('i_fb', -150, -20), ('i_rstref_n', -150, 20), ('i_rstfb_n', -150, 60)],outp=[('o_upn', 150, -60), ('o_dnn', 150, -20)])
properties = {} #voor netlisten
#view variables:
iconSource = 'pfd'
textSource = 'libraries/library_testlib/pfd.py'



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