# cell definition
# name = 'DO'
# libname = 'comedi'

inp = 1
outp = 0

parameters = dict() #parametriseerbare cell
properties = {'Device': " '/dev/comedi0'", 'Threshold': ' 1.0', 'name': 'comediDOBlk', 'Channel': ' 0'} #voor netlisten
#view variables:
iconSource = 'DO'


views = {'icon':iconSource}
