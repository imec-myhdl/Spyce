name = 'test1' #zelfde als bestand naam 
libname = 'testlib' #zelfde als map naam

inp = [('a', -40, -20), ('b', -40, 20)]
outp = [('z', 40, 0)]

parameters = ['inp', 'outp'] #parametriseerbare cell
properties = {'name': 'sumBlk', 'Gains': ' [1,-1]'} #voor netlisten
#view variables:
iconSource = 'test1'
textSource = 'libraries/library_testlib/test1.py'


views = {'icon':iconSource,'text':textSource}