name = 'Saturation' #zelfde als bestand naam 
libname = 'common' #zelfde als map naam

inp = 1
outp = 1

parameters = None #parametriseerbare cell
properties = {'Lower saturation': ' -10', 'Upper saturation': '10', 'name': 'saturBlk'} #voor netlisten
#view variables:
iconSource = 'SATUR'
textSource = 'libraries/library_common/Saturation.py'


views = {'icon':iconSource,'text':textSource}
