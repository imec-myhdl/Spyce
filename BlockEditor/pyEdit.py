#!/usr/bin/python
import sys, os

# check Qt if already loaded (e.g. when running inside spyder or other program)
if 'QT_PREFERRED_BINDING' not in os.environ:
    mods = ' '.join(sys.modules.keys())
    for k in ['PyQt4', 'PySide', 'PyQt5', 'PySide2']:
        if k in mods:
            os.environ['QT_PREFERRED_BINDING'] = k
            print ('using {}'.format(k))
            break
        
import subprocess
exist = subprocess.call('command -v '+ 'inkscape' + '>> /dev/null', shell=True)
if exist == 0:
    print ('inkscape present')
else:
    print ('Warning: inkscape is nor installed, you will not be able to edit icons')

from supsisim.pysim import supsisimul
#from control import *

if __name__ == "__main__":
    if len(sys.argv) > 1:
        fname = sys.argv[1]
    else:
        fname = 'untitled'
    th = supsisimul(fname, runflag = True)
    th.start()
    th.join()

