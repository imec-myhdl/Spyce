# cell definition
# name = 'DA'
# libname = 'comedi'

inp = 1
outp = 0

parameters = dict() #parametriseerbare cell
properties = {'Device': " '/dev/comedi0'", 'Range': ' 0', 'name': 'comediDABlk', 'Channel': ' 0'} #voor netlisten
#view variables:
iconSource = 'DA'


views = {'icon':iconSource}
