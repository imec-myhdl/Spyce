name = 'module' #same as file name (without .py) 
libname = 'symbols' #same as directory name 

inp = [(u'i_pin0', -40, 0)]
outp = [(u'o_pin0', 40, 0)]

parameters = {} #programmable cell
properties = {} #netlist properties
#view variables:
iconSource = 'SUM'
textSource = 'libraries/library_symbols/module.py'


views = {'icon':iconSource,'text':textSource}