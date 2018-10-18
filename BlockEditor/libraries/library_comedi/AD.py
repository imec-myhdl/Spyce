# cell definition
# name = 'AD'
# libname = 'comedi'

inp = 0
outp = 1

parameters = dict() #parametriseerbare cell
properties = {'Device': " '/dev/comedi0'", 'Range': ' 0', 'name': 'comediADBlk', 'Channel': ' 0'} #voor netlisten
#view variables:
iconSource = 'AD'


views = {'icon':iconSource}
