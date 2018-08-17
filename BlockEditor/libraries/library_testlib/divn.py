name = 'divn' #zelfde als bestand naam 
libname = 'testlib' #zelfde als map naam

inp = [('i_clk_in', -150, -40), ('i_rst_an', -150, 0), ('i_div', -150, 40)]
outp = [('o_clk_out', 150, -40)]

parameters = ['inp', 'outp'] #parametriseerbare cell
properties = {} #voor netlisten
#view variables:
iconSource = 'divn'
textSource = 'libraries/library_testlib/divn.py'


views = {'icon':iconSource,'text':textSource}