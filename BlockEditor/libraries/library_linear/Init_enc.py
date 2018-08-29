name = 'Init_enc' #zelfde als bestand naam 
libname = 'linear' #zelfde als map naam

inp = 1
outp = 1

parameters = dict() #parametriseerbare cell
properties = {'Default Output': ' 0', 'Trigger Time': ' 1', 'name': 'init_encBlk', 'Offset': ' 0'} #voor netlisten
#view variables:
iconSource = 'INIT'
textSource = 'libraries/library_linear/Init_enc.py'


views = {'icon':iconSource,'text':textSource}