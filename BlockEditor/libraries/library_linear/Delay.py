name = 'Delay' #zelfde als bestand naam 
libname = 'linear' #zelfde als map naam

inp = 1
outp = 1

parameters = dict() #parametriseerbare cell
properties = {'Initial conditions': ' 0', 'name': 'zdelayBlk'} #voor netlisten
#view variables:
iconSource = 'DELAY'
textSource = 'libraries/library_linear/Delay.py'


views = {'icon':iconSource,'text':textSource}