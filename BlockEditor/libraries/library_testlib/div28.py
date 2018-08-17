name = 'div28' #zelfde als bestand naam 
libname = 'testlib' #zelfde als map naam

inp = [('i_cp', -150, -120), ('i_cn', -150, -80), ('i_ena_lo', -150, -40)]
outp = [('o_div2', 150, -120), ('o_div8', 150, -80), ('o_div16', 150, -40), ('o_p000', 150, 0), ('o_p090', 150, 40), ('o_p180', 150, 80), ('o_p270', 150, 120)]

parameters = ['inp', 'outp'] #parametriseerbare cell
properties = {} #voor netlisten
#view variables:
iconSource = 'div28'
textSource = 'libraries/library_testlib/div28.py'


views = {'icon':iconSource,'text':textSource}