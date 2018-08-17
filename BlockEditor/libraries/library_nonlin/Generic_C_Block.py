name = 'Generic_C_Block' #zelfde als bestand naam 
libname = 'nonlin' #zelfde als map naam

inp = 1
outp = 1

parameters = ['inp', 'outp'] #parametriseerbare cell
properties = {'String': " ''", 'States': ' [0,0]', ' Int pars': '[]', 'Real pars': ' []', ' Function name': " 'test'", 'FeedForw': ' 0', 'name': 'genericBlk'} #voor netlisten
#view variables:
iconSource = 'CBLOCK'
textSource = 'libraries/library_nonlin/Generic_C_Block.py'


views = {'icon':iconSource,'text':textSource}