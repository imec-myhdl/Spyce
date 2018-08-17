name = 'LTI_continous' #zelfde als bestand naam 
libname = 'linear' #zelfde als map naam

inp = 1
outp = 1

parameters = ['inp', 'outp'] #parametriseerbare cell
properties = {'Initial conditions': ' 0', 'name': 'cssBlk', 'System': ' sys'} #voor netlisten
#view variables:
iconSource = 'CSS'
textSource = 'libraries/library_linear/LTI_continous.py'


views = {'icon':iconSource,'text':textSource}