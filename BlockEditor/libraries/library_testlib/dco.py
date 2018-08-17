name = 'dco' #zelfde als bestand naam 
libname = 'testlib' #zelfde als map naam

inp = [('i_pvt', -150, -60), ('i_acq', -150, -20), ('i_trk', -150, 20), ('i_mod', -150, 60)]
outp = [('o_lop', 150, -60), ('o_lon', 150, -20)]

parameters = ['inp', 'outp'] #parametriseerbare cell
properties = {} #voor netlisten
#view variables:
iconSource = 'dco'
textSource = 'libraries/library_testlib/dco.py'


views = {'icon':iconSource,'text':textSource}