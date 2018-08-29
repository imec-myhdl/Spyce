name = 'Epos_mot_X' #zelfde als bestand naam 
libname = 'can' #zelfde als map naam

inp = 1
outp = 0

parameters = dict() #parametriseerbare cell
properties = {'Deriv. gain': ' 238', 'Vel. FeedForw': ' 0', 'name': 'epos_MotXBlk', 'Device ID': ' 0x01', 'Acc. Feed Forw.': '1', 'Prop. gain': ' 126', 'Integ. gain': ' 325'} #voor netlisten
#view variables:
iconSource = 'MOT_X'
textSource = 'libraries/library_can/Epos_mot_X.py'


views = {'icon':iconSource,'text':textSource}