name = 'Mclm_enc' #zelfde als bestand naam 
libname = 'can' #zelfde als map naam

inp = 0
outp = 1

parameters = None #parametriseerbare cell
properties = {'Device ID': ' 0x01', 'Resolution': ' 125000', 'name': 'MCLM_EncBlk'} #voor netlisten
#view variables:
iconSource = 'ENC'
textSource = 'libraries/library_can/Mclm_enc.py'


views = {'icon':iconSource,'text':textSource}