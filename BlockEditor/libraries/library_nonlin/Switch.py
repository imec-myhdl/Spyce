name = 'Switch' #zelfde als bestand naam 
libname = 'nonlin' #zelfde als map naam

inp = 3
outp = 1

parameters = dict() #parametriseerbare cell
properties = {'Condition [0 < or 1 >] ': ' 0', 'Compare Value': ' 0.5', 'Persistence [0 no or 1 yes]': ' 0', 'name': 'switchBlk'} #voor netlisten
#view variables:
iconSource = 'SWITCH'
textSource = 'libraries/library_nonlin/Switch.py'


views = {'icon':iconSource,'text':textSource}