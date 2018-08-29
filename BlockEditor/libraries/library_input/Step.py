name = 'Step' #zelfde als bestand naam 
libname = 'input' #zelfde als map naam

inp = 0
outp = 1

parameters = dict() #parametriseerbare cell
properties = {'Step Time': ' 1', 'name': 'stepBlk', 'Step Value': ' 1'} #voor netlisten
#view variables:
iconSource = 'STEP'
textSource = 'libraries/library_input/Step.py'


views = {'icon':iconSource,'text':textSource}