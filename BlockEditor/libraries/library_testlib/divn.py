name = 'divn' #zelfde als bestand naam 
libname = 'testlib' #zelfde als map naam

inp = [('i_clk_in', -150, -40), ('i_rst_an', -150, 0), ('i_div', -150, 40)]
outp = [('o_clk_out', 150, -40)]

parameters = dict(inp=[('i_clk_in', -150, -40), ('i_rst_an', -150, 0), ('i_div', -150, 40)],outp=[('o_clk_out', 150, -40)])
properties = {} #voor netlisten
#view variables:
iconSource = 'divn'
textSource = 'libraries/library_testlib/divn.py'



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