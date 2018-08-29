name = 'DO' #zelfde als bestand naam 
libname = 'comedi' #zelfde als map naam

inp = 1
outp = 0

parameters = dict() #parametriseerbare cell
properties = {'Device': " '/dev/comedi0'", 'Threshold': ' 1.0', 'name': 'comediDOBlk', 'Channel': ' 0'} #voor netlisten
#view variables:
iconSource = 'DO'
textSource = 'libraries/library_comedi/DO.py'


views = {'icon':iconSource,'text':textSource}
