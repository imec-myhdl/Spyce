name = 'Sum' #zelfde als bestand naam 
libname = 'common' #zelfde als map naam

inp = 2
outp = 1

parameters = ['inp', 'outp'] #parametriseerbare cell
properties = {'name': 'sumBlk', 'Gains': ' [1,-1]'} #voor netlisten
#view variables:
iconSource = 'SUM'
textSource = 'libraries/library_common/Sum.py'


views = {'icon':iconSource,'text':textSource}