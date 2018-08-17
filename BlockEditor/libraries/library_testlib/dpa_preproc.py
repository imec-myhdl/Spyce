name = 'dpa_preproc' #zelfde als bestand naam 
libname = 'testlib' #zelfde als map naam

inp = [('i_clk_lo', -150, -200), ('i_clk_hi', -150, -160), ('i_rst_an', -150, -120), ('i_en', -150, -80), ('i_ble_en', -150, -40), ('i_dia', -150, 0), ('i_di', -150, 40), ('i_del_en', -150, 80), ('i_bypass_en', -150, 120), ('i_bypass_base', -150, 160), ('i_bypass_delta', -150, 200)]
outp = [('o_pa_base_hi_th', 150, -200), ('o_pa_base_lo_bin', 150, -160), ('o_pa_delta_0', 150, -120), ('o_pa_delta_1', 150, -80), ('o_pa_delta_2', 150, -40), ('o_pa_delta_3', 150, 0)]

parameters = ['inp', 'outp'] #parametriseerbare cell
properties = {} #voor netlisten
#view variables:
iconSource = 'dpa_preproc'
textSource = 'libraries/library_testlib/dpa_preproc.py'


views = {'icon':iconSource,'text':textSource}