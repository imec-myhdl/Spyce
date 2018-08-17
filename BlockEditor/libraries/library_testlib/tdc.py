name = 'tdc' #zelfde als bestand naam 
libname = 'testlib' #zelfde als map naam

inp = [('i_ref', -150, -100), ('i_refd_n', -150, -60), ('i_fb', -150, -20), ('i_fbd_n', -150, 20), ('i_cap_ref', -150, 60), ('i_cap_fb', -150, 100)]
outp = [('o_tdc', 150, -100), ('o_sample_fb', 150, -60), ('o_cnt_fb', 150, -20), ('o_ckdig', 150, 20), ('o_rstpfd_n', 150, 60), ('o_rstcap', 150, 100)]

parameters = ['inp', 'outp'] #parametriseerbare cell
properties = {} #voor netlisten
#view variables:
iconSource = 'tdc'
textSource = 'libraries/library_testlib/tdc.py'


views = {'icon':iconSource,'text':textSource}