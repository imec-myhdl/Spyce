name = 'FMU' #zelfde als bestand naam 
libname = 'nonlin' #zelfde als map naam

inp = 1
outp = 1

parameters = ['inp', 'outp'] #parametriseerbare cell
properties = {'Major step': ' 0.01', 'Feedthrough': ' 0', 'OUT_REF': " ['y']", 'IN_REF': " ['u']", 'FMU_NAME': " ''", 'name': 'FmuBlk'} #voor netlisten
#view variables:
iconSource = 'FMU'
textSource = 'libraries/library_nonlin/FMU.py'


views = {'icon':iconSource,'text':textSource}