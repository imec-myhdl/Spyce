name = 'div28' #zelfde als bestand naam 
libname = 'testlib' #zelfde als map naam

inp = [('i_cp', -150, -120), ('i_cn', -150, -80), ('i_ena_lo', -150, -40)]
outp = [('o_div2', 150, -120), ('o_div8', 150, -80), ('o_div16', 150, -40), ('o_p000', 150, 0), ('o_p090', 150, 40), ('o_p180', 150, 80), ('o_p270', 150, 120)]

parameters = dict(inp=[('i_cp', -150, -120), ('i_cn', -150, -80), ('i_ena_lo', -150, -40)],outp=[('o_div2', 150, -120), ('o_div8', 150, -80), ('o_div16', 150, -40), ('o_p000', 150, 0), ('o_p090', 150, 40), ('o_p180', 150, 80), ('o_p270', 150, 120)])
properties = {} #voor netlisten
#view variables:
iconSource = 'div28'
textSource = 'libraries/library_testlib/div28.py'



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