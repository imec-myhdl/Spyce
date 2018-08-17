name = 'Gain' #zelfde als bestand naam 
libname = 'common' #zelfde als map naam

inp = 1
outp = 1

parameters = ['inp', 'outp'] #parametriseerbare cell
properties = {'name': 'matmultBlk', 'Gains': ' 1'} #voor netlisten
#view variables:
iconSource = 'MULT'
textSource = 'libraries/library_common/Gain.py'


views = {'icon':iconSource,'text':textSource}