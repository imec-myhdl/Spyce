# cell definition
# name = 'DI'
# libname = 'comedi'

inp = 0
outp = 1

parameters = dict() #parametriseerbare cell
properties = {'Device': " '/dev/comedi0'", 'name': 'comediDIBlk', 'Channel': ' 0'} #voor netlisten
#view variables:
iconSource = 'DI'


views = {'icon':iconSource}
