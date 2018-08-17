name = 'lo_divider' #zelfde als bestand naam 
libname = 'testlib' #zelfde als map naam

inp = [('i_LOP', -150, -140), ('i_LON', -150, -100)]
outp = [('o_LOP_PD', 150, -140), ('o_LON_PD', 150, -100), ('o_LOP_RF', 150, -60), ('o_LON_RF', 150, -20), ('o_LOP_AM', 150, 20), ('o_LON_AM', 150, 60), ('o_LON_HS_DBB', 150, 100), ('o_LOP_HS_DBB', 150, 140)]

parameters = ['inp', 'outp'] #parametriseerbare cell
properties = {} #voor netlisten
#view variables:
iconSource = 'lo_divider'
textSource = 'libraries/library_testlib/lo_divider.py'


views = {'icon':iconSource,'text':textSource}