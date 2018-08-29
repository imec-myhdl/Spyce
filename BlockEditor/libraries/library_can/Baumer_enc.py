name = 'Baumer_enc' #zelfde als bestand naam 
libname = 'can' #zelfde als map naam

inp = 0
outp = 1

parameters = dict() #parametriseerbare cell
properties = {'Device ID': ' 0x01', 'Resolution': ' 500', 'name': 'baumer_EncBlk'} #voor netlisten
#view variables:
iconSource = 'ENC'
textSource = 'libraries/library_can/Baumer_enc.py'
myhdlSource = 'libraries/library_can/Baumer_enc_myhdl.py'


views = {'icon':iconSource,'text':textSource,'myhdl':myhdlSource}