name = 'Epos_AD' #zelfde als bestand naam 
libname = 'can' #zelfde als map naam

inp = 0
outp = 1

parameters = dict() #parametriseerbare cell
properties = {'Device ID': ' 0x01', 'Channel [0/1]': ' 0', 'name': 'epos_areadBlk'} #voor netlisten
#view variables:
iconSource = 'AD'
textSource = 'libraries/library_can/Epos_AD.py'


views = {'icon':iconSource,'text':textSource}