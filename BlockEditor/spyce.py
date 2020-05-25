#!/usr/bin/env python

# Standard library imports
from __future__ import print_function
import os, sys
import subprocess

# Third party imports
# check Qt if already loaded (e.g. when running inside spyder or other program)
if 'QT_PREFERRED_BINDING' not in os.environ:
    mods = ' '.join(list(sys.modules.keys()))
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

    cwd = os.getcwd()
    library_path = os.path.join(cwd, 'libraries')

    if not os.path.isdir(library_path):
        print ('creating initial setup')
        os.makedirs(library_path, mode=0o770)
        source_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libraries')
        for fn in os.listdir(source_dir):
            if fn.startswith('library_') or fn == '__init__.py':
                src = os.path.join(source_dir, fn)
                dst = os.path.join(library_path, fn)
                os.symlink(src, dst)


    if not os.path.isfile('settings.py'):
        print('You do not have a configuration file. You might want to create "settings.py"')
        print('it is used as an extension to the default file (.../Spyce/BlockEditor/supsisim/const.py)')
    if len(sys.argv) > 1:
        fname = sys.argv[1]
    else:
        fname = 'untitled'
    th = supsisimul(fname, runflag = True)
    th.start()
    th.join()

