name = 'Saturation' #zelfde als bestand naam 
libname = 'nonlin' #zelfde als map naam

inp = 1
outp = 1

parameters = dict() #parametriseerbare cell
properties = {'Lower saturation': ' -10', 'Upper saturation': '10', 'name': 'saturBlk'} #voor netlisten
#view variables:
iconSource = 'SATUR'
textSource = 'libraries/library_nonlin/Saturation.py'


views = {'icon':iconSource,'text':textSource}