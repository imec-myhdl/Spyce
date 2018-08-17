name = 'LTI_discrete' #zelfde als bestand naam 
libname = 'linear' #zelfde als map naam

inp = 1
outp = 1

parameters = ['inp', 'outp'] #parametriseerbare cell
properties = {'Initial conditions': ' 0', 'name': 'dssBlk', 'System': ' sys'} #voor netlisten
#view variables:
iconSource = 'DSS'
textSource = 'libraries/library_linear/LTI_discrete.py'


views = {'icon':iconSource,'text':textSource}