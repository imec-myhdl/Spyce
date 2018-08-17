name = 'Maxon_mot_I' #zelfde als bestand naam 
libname = 'can' #zelfde als map naam

inp = 1
outp = 0

parameters = None #parametriseerbare cell
properties = {'Device ID': ' 0x01', 'Prop. gain': ' 2200', 'Integ. gain': ' 500', 'name': 'maxon_MotBlk'} #voor netlisten
#view variables:
iconSource = 'MOT_I'
textSource = 'libraries/library_can/Maxon_mot_I.py'


views = {'icon':iconSource,'text':textSource}