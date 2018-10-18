# cell definition
# name = 'Saturation'
# libname = 'nonlin'

inp = 1
outp = 1

parameters = dict() #parametriseerbare cell
properties = {'Lower saturation': ' -10', 'Upper saturation': '10', 'name': 'saturBlk'} #voor netlisten
#view variables:
iconSource = 'SATUR'


views = {'icon':iconSource}
