name = 'Mclm_CO_mot_X' #zelfde als bestand naam 
libname = 'can' #zelfde als map naam

inp = 1
outp = 0

parameters = None #parametriseerbare cell
properties = {'Device ID': ' 0x01', 'Resolution': ' 125000', 'name': 'MCLM_CO_MotXBlk'} #voor netlisten
#view variables:
iconSource = 'MOT_X'
textSource = 'libraries/library_can/Mclm_CO_mot_X.py'


views = {'icon':iconSource,'text':textSource}