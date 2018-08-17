name = 'dpa_preproc_6bPA' #zelfde als bestand naam 
libname = 'testlib' #zelfde als map naam

inp = [('w_LOP_RF', -150, -180), ('w_LON_RF', -150, -140), ('w_LOP_HS_DBB', -150, -100), ('w_LOP_AM', -150, -60), ('w_LON_AM', -150, -20), ('i_modulation_enable', -150, 20), ('i_modulation_AM_data', -150, 60), ('i_rst_an', -150, 100), ('i_rst_n', -150, 140), ('i_del_en', -150, 180)]
outp = [('o_pa_base_hi_th', 150, -180), ('o_pa_base_lo_bin', 150, -140)]

parameters = ['inp', 'outp'] #parametriseerbare cell
properties = {} #voor netlisten
#view variables:
iconSource = 'dpa_preproc_6bPA'
textSource = 'libraries/library_testlib/dpa_preproc_6bPA.py'


views = {'icon':iconSource,'text':textSource}