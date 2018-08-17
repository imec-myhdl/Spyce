name = 'Socket' #zelfde als bestand naam 
libname = 'Socket' #zelfde als map naam

inp = 0
outp = 1

parameters = ['inp', 'outp'] #parametriseerbare cell
properties = {'name': 'unixsocketSBlk', 'Default outputs': '[0.]', 'Socket': " 'ssock'"} #voor netlisten
#view variables:
iconSource = 'SOCK'
textSource = 'libraries/library_Socket/Socket.py'


views = {'icon':iconSource,'text':textSource}