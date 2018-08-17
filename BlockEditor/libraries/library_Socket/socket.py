name = 'socket' #zelfde als bestand naam 
libname = 'Socket' #zelfde als map naam

inp = 1
outp = 0

parameters = ['inp', 'outp'] #parametriseerbare cell
properties = {'name': 'unixsocketCBlk', 'Socket': " 'bsock'"} #voor netlisten
#view variables:
iconSource = 'SOCK'
textSource = 'libraries/library_Socket/socket.py'


views = {'icon':iconSource,'text':textSource}