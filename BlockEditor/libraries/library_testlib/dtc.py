name = 'dtc' #zelfde als bestand naam 
libname = 'testlib' #zelfde als map naam

inp = [('i_clk_in', -150, -60), ('i_dtc_row', -150, -20), ('i_dtc_col', -150, 20), ('i_phase_sel', -150, 60)]
outp = [('o_clk_out', 150, -60), ('o_phase_sel', 150, -20)]

parameters = dict(inp=[('i_clk_in', -150, -60), ('i_dtc_row', -150, -20), ('i_dtc_col', -150, 20), ('i_phase_sel', -150, 60)],outp=[('o_clk_out', 150, -60), ('o_phase_sel', 150, -20)])
properties = {} #voor netlisten
#view variables:
iconSource = 'dtc'
textSource = 'libraries/library_testlib/dtc.py'



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