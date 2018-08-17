name = 'Gain' #zelfde als bestand naam 
libname = 'linear' #zelfde als map naam

inp = 1
outp = 1

parameters = ['inp', 'outp'] #parametriseerbare cell
properties = {'name': 'matmultBlk', 'Gains': ' 1'} #voor netlisten
#view variables:
iconSource = 'MULT'
textSource = 'libraries/library_linear/Gain.py'


views = {'icon':iconSource,'text':textSource}