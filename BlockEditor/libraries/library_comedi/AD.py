name = 'AD' #zelfde als bestand naam 
libname = 'comedi' #zelfde als map naam

inp = 0
outp = 1

parameters = None #parametriseerbare cell
properties = {'Device': " '/dev/comedi0'", 'Range': ' 0', 'name': 'comediADBlk', 'Channel': ' 0'} #voor netlisten
#view variables:
iconSource = 'AD'
textSource = 'libraries/library_comedi/AD.py'


views = {'icon':iconSource,'text':textSource}