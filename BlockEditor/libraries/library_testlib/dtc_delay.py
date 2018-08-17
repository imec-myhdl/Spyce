name = 'dtc_delay' #zelfde als bestand naam 
libname = 'testlib' #zelfde als map naam

inp = [('i_a', -150, -60), ('i_row', -150, -20), ('i_col', -150, 20), ('i_res_tune', -150, 60)]
outp = [('o_zn', 150, -60)]

parameters = ['inp', 'outp'] #parametriseerbare cell
properties = {} #voor netlisten
#view variables:
iconSource = 'dtc_delay'
textSource = 'libraries/library_testlib/dtc_delay.py'


views = {'icon':iconSource,'text':textSource}