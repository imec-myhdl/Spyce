name = 'dtc' #zelfde als bestand naam 
libname = 'testlib' #zelfde als map naam

inp = [('i_clk_in', -150, -60), ('i_dtc_row', -150, -20), ('i_dtc_col', -150, 20), ('i_phase_sel', -150, 60)]
outp = [('o_clk_out', 150, -60), ('o_phase_sel', 150, -20)]

parameters = ['inp', 'outp'] #parametriseerbare cell
properties = {} #voor netlisten
#view variables:
iconSource = 'dtc'
textSource = 'libraries/library_testlib/dtc.py'


views = {'icon':iconSource,'text':textSource}