name = 'dpa_preproc_6bPA' #zelfde als bestand naam 
libname = 'testlib' #zelfde als map naam

inp = [('w_LOP_RF', -150, -180), ('w_LON_RF', -150, -140), ('w_LOP_HS_DBB', -150, -100), ('w_LOP_AM', -150, -60), ('w_LON_AM', -150, -20), ('i_modulation_enable', -150, 20), ('i_modulation_AM_data', -150, 60), ('i_rst_an', -150, 100), ('i_rst_n', -150, 140), ('i_del_en', -150, 180)]
outp = [('o_pa_base_hi_th', 150, -180), ('o_pa_base_lo_bin', 150, -140)]

parameters = dict(inp=[('w_LOP_RF', -150, -180), ('w_LON_RF', -150, -140), ('w_LOP_HS_DBB', -150, -100), ('w_LOP_AM', -150, -60), ('w_LON_AM', -150, -20), ('i_modulation_enable', -150, 20), ('i_modulation_AM_data', -150, 60), ('i_rst_an', -150, 100), ('i_rst_n', -150, 140), ('i_del_en', -150, 180)],outp=[('o_pa_base_hi_th', 150, -180), ('o_pa_base_lo_bin', 150, -140)])
properties = {} #voor netlisten
#view variables:
iconSource = 'dpa_preproc_6bPA'
textSource = 'libraries/library_testlib/dpa_preproc_6bPA.py'



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