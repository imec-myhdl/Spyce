name = 'PulseGenerator' #zelfde als bestand naam 
libname = 'input' #zelfde als map naam

inp = 0
outp = 1

parameters = dict() #parametriseerbare cell
properties = {'name': 'squareBlk', 'Period': ' 4', 'Delay': ' 0', 'Width': ' 2', 'Bias': ' 0', 'Amplitude': ' 1'} #voor netlisten
#view variables:
iconSource = 'SQUARE'
textSource = 'libraries/library_input/PulseGenerator.py'


views = {'icon':iconSource,'text':textSource}