name = 'Lookup' #zelfde als bestand naam 
libname = 'nonlin' #zelfde als map naam

inp = 1
outp = 1

parameters = dict() #parametriseerbare cell
properties = {'Coeff ': ' [1,0]', 'name': 'lutBlk'} #voor netlisten
#view variables:
iconSource = 'LOOKUP'
textSource = 'libraries/library_nonlin/Lookup.py'


views = {'icon':iconSource,'text':textSource}