name = 'pfd' #zelfde als bestand naam 
libname = 'testlib' #zelfde als map naam

inp = [('i_ref', -150, -60), ('i_fb', -150, -20), ('i_rstref_n', -150, 20), ('i_rstfb_n', -150, 60)]
outp = [('o_upn', 150, -60), ('o_dnn', 150, -20)]

parameters = ['inp', 'outp'] #parametriseerbare cell
properties = {} #voor netlisten
#view variables:
iconSource = 'pfd'
textSource = 'libraries/library_testlib/pfd.py'


views = {'icon':iconSource,'text':textSource}