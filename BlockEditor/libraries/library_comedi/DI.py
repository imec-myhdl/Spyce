name = 'DI' #zelfde als bestand naam 
libname = 'comedi' #zelfde als map naam

inp = 0
outp = 1

parameters = None #parametriseerbare cell
properties = {'Device': " '/dev/comedi0'", 'name': 'comediDIBlk', 'Channel': ' 0'} #voor netlisten
#view variables:
iconSource = 'DI'
textSource = 'libraries/library_comedi/DI.py'


views = {'icon':iconSource,'text':textSource}