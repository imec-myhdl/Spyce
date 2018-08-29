name = 'dpa_preproc' #zelfde als bestand naam 
libname = 'testlib' #zelfde als map naam

inp = [('i_clk_lo', -150, -200), ('i_clk_hi', -150, -160), ('i_rst_an', -150, -120), ('i_en', -150, -80), ('i_ble_en', -150, -40), ('i_dia', -150, 0), ('i_di', -150, 40), ('i_del_en', -150, 80), ('i_bypass_en', -150, 120), ('i_bypass_base', -150, 160), ('i_bypass_delta', -150, 200)]
outp = [('o_pa_base_hi_th', 150, -200), ('o_pa_base_lo_bin', 150, -160), ('o_pa_delta_0', 150, -120), ('o_pa_delta_1', 150, -80), ('o_pa_delta_2', 150, -40), ('o_pa_delta_3', 150, 0)]

parameters = dict(inp=[('i_clk_lo', -150, -200), ('i_clk_hi', -150, -160), ('i_rst_an', -150, -120), ('i_en', -150, -80), ('i_ble_en', -150, -40), ('i_dia', -150, 0), ('i_di', -150, 40), ('i_del_en', -150, 80), ('i_bypass_en', -150, 120), ('i_bypass_base', -150, 160), ('i_bypass_delta', -150, 200)],outp=[('o_pa_base_hi_th', 150, -200), ('o_pa_base_lo_bin', 150, -160), ('o_pa_delta_0', 150, -120), ('o_pa_delta_1', 150, -80), ('o_pa_delta_2', 150, -40), ('o_pa_delta_3', 150, 0)])
properties = {} #voor netlisten
#view variables:
iconSource = 'dpa_preproc'
textSource = 'libraries/library_testlib/dpa_preproc.py'



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