name = 'lelijkdiagrammetje' #same as file name (without .py) 
libname = 'symbols' #same as directory name

inp = []
outp = []

parameters = {} #programmable cell
properties = {} #netlist properties
#view variables:
iconSource = 'STEP'
myhdlSource = 'libraries/library_symbols/lelijkdiagrammetje_myhdl.py'
diagramSource = 'libraries/library_symbols/lelijkdiagrammetje_diagram.py'
textSource = 'libraries/library_symbols/lelijkdiagrammetje.py'


views = {'myhdl':myhdlSource,'icon':iconSource,'diagram':diagramSource,'text':textSource}