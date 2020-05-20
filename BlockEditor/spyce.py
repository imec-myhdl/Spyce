#!/usr/bin/python

# Standard library imports
import os, sys
import subprocess

# Third party imports
# check Qt if already loaded (e.g. when running inside spyder or other program)
if 'QT_PREFERRED_BINDING' not in os.environ:
    mods = ' '.join(sys.modules.keys())
    for k in ['PyQt4', 'PySide', 'PyQt5', 'PySide2']:
        if k in mods:
            os.environ['QT_PREFERRED_BINDING'] = k
            break
    os.environ['QT_PREFERRED_BINDING'] =  os.pathsep.join(['PyQt4', 'PySide', 'PyQt5', 'PySide2'])   
    

import Qt # see https://github.com/mottosso/Qt.py     

# Local application imports
from supsisim.pysim import supsisimul

# main
if __name__ == "__main__":
    print ('using {}, python = {}.{}, Qt  = {}'.format(Qt.__binding__, sys.version_info[0], sys.version_info[1], Qt.__binding_version__ ))
    exist = subprocess.call('command -v '+ 'inkscape' + '>> /dev/null', shell=True)
    if exist == 0:
        print ('inkscape present')
    else:
        print ('Warning: inkscape is not installed, you will not be able to edit icons')
    if len(sys.argv) > 1:
        fname = sys.argv[1]
    else:
        fname = 'untitled'
    th = supsisimul(fname, runflag = True)
    th.start()
    th.join()

