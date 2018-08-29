name = 'tdc' #zelfde als bestand naam 
libname = 'testlib' #zelfde als map naam

inp = [('i_ref', -150, -100), ('i_refd_n', -150, -60), ('i_fb', -150, -20), ('i_fbd_n', -150, 20), ('i_cap_ref', -150, 60), ('i_cap_fb', -150, 100)]
outp = [('o_tdc', 150, -100), ('o_sample_fb', 150, -60), ('o_cnt_fb', 150, -20), ('o_ckdig', 150, 20), ('o_rstpfd_n', 150, 60), ('o_rstcap', 150, 100)]

parameters = dict(inp=[('i_ref', -150, -100), ('i_refd_n', -150, -60), ('i_fb', -150, -20), ('i_fbd_n', -150, 20), ('i_cap_ref', -150, 60), ('i_cap_fb', -150, 100)],outp=[('o_tdc', 150, -100), ('o_sample_fb', 150, -60), ('o_cnt_fb', 150, -20), ('o_ckdig', 150, 20), ('o_rstpfd_n', 150, 60), ('o_rstcap', 150, 100)])
properties = {} #voor netlisten
#view variables:
iconSource = 'tdc'
textSource = 'libraries/library_testlib/tdc.py'



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