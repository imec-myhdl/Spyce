name = 'DA' #zelfde als bestand naam 
libname = 'comedi' #zelfde als map naam

inp = 1
outp = 0

parameters = dict() #parametriseerbare cell
properties = {'Device': " '/dev/comedi0'", 'Range': ' 0', 'name': 'comediDABlk', 'Channel': ' 0'} #voor netlisten
#view variables:
iconSource = 'DA'
textSource = 'libraries/library_comedi/DA.py'


views = {'icon':iconSource,'text':textSource}