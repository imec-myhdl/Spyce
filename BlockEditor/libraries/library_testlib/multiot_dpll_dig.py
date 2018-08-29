name = 'multiot_dpll_dig' #zelfde als bestand naam 
libname = 'testlib' #zelfde als map naam

inp = [('i_clk', -150, -220), ('clk_HS_DBB', -150, -180), ('i_rst_an', -150, -140), ('i_ch_sw', -150, -100), ('i_modulation_enable', -150, -60), ('i_modulation_PM_data', -150, -20), ('i_modulation_FM_data', -150, 20), ('i_tdc', -150, 60), ('i_cnt_fb', -150, 100), ('i_cnt_ref', -150, 140), ('w_rst_n', -150, 180), ('w_fcw', -150, 220)]
outp = [('o_dco_pvt', 150, -220), ('o_dco_acq', 150, -180), ('o_dco_trk', 150, -140), ('o_dco_mod', 150, -100), ('o_n', 150, -60), ('o_dtc_ref_row', 150, -20), ('o_dtc_ref_col', 150, 20), ('o_dtc_fb_row', 150, 60), ('o_dtc_fb_col', 150, 100)]

parameters = dict(inp=[('i_clk', -150, -220), ('clk_HS_DBB', -150, -180), ('i_rst_an', -150, -140), ('i_ch_sw', -150, -100), ('i_modulation_enable', -150, -60), ('i_modulation_PM_data', -150, -20), ('i_modulation_FM_data', -150, 20), ('i_tdc', -150, 60), ('i_cnt_fb', -150, 100), ('i_cnt_ref', -150, 140), ('w_rst_n', -150, 180), ('w_fcw', -150, 220)],outp=[('o_dco_pvt', 150, -220), ('o_dco_acq', 150, -180), ('o_dco_trk', 150, -140), ('o_dco_mod', 150, -100), ('o_n', 150, -60), ('o_dtc_ref_row', 150, -20), ('o_dtc_ref_col', 150, 20), ('o_dtc_fb_row', 150, 60), ('o_dtc_fb_col', 150, 100)])
properties = {} #voor netlisten
#view variables:
iconSource = 'multiot_dpll_dig'
textSource = 'libraries/library_testlib/multiot_dpll_dig.py'



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