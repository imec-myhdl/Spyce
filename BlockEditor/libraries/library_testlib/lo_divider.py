name = 'lo_divider' #zelfde als bestand naam 
libname = 'testlib' #zelfde als map naam

inp = [('i_LOP', -150, -140), ('i_LON', -150, -100)]
outp = [('o_LOP_PD', 150, -140), ('o_LON_PD', 150, -100), ('o_LOP_RF', 150, -60), ('o_LON_RF', 150, -20), ('o_LOP_AM', 150, 20), ('o_LON_AM', 150, 60), ('o_LON_HS_DBB', 150, 100), ('o_LOP_HS_DBB', 150, 140)]

parameters = dict(inp=[('i_LOP', -150, -140), ('i_LON', -150, -100)],outp=[('o_LOP_PD', 150, -140), ('o_LON_PD', 150, -100), ('o_LOP_RF', 150, -60), ('o_LON_RF', 150, -20), ('o_LOP_AM', 150, 20), ('o_LON_AM', 150, 60), ('o_LON_HS_DBB', 150, 100), ('o_LOP_HS_DBB', 150, 140)])
properties = {} #voor netlisten
#view variables:
iconSource = 'lo_divider'
textSource = 'libraries/library_testlib/lo_divider.py'



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