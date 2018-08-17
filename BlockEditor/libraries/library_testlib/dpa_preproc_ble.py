name = 'dpa_preproc_ble' #zelfde als bestand naam 
libname = 'testlib' #zelfde als map naam

inp = [('w_LOP_RF', -150, -120), ('w_LON_RF', -150, -80), ('w_LOP_AM', -150, -40), ('i_modulation_enable', -150, 0), ('i_modulation_AM_data', -150, 40), ('i_rst_an', -150, 80), ('i_rst_n', -150, 120)]
outp = [('w_am_data', 150, -120)]

parameters = ['inp', 'outp'] #parametriseerbare cell
properties = {} #voor netlisten
#view variables:
iconSource = 'dpa_preproc_ble'
textSource = 'libraries/library_testlib/dpa_preproc_ble.py'


views = {'icon':iconSource,'text':textSource}