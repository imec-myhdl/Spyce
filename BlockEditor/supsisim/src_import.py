# -*- coding: utf-8 -*-
"""
utility to streamline the (re) importing of files
"""

import os, sys


def import_module_from_source_file(filepath):
    fullpath       = os.path.abspath(filepath)
    path, filename = os.path.split(fullpath)
    modname, ext     = os.path.splitext(filename) # modname could be anything, but this seems cleanest

    if sys.version_info >= (2,7) and sys.version_info < (3,0):
        # python 2
        try:
            import imp
            mod = imp.load_source(modname, fullpath)
        except:
            mod = None
            raise Exception('loading of {} caused error:\n{}'.format(fullpath, sys.exc_info()))

    elif sys.version_info >= (3,3) and sys.version_info < (3,5):
        # python 3.3 or 3.4
        try:
            from importlib.machinery import SourceFileLoader
            mod = SourceFileLoader(modname, fullpath).load_module()
        except:
            mod = None
            raise Exception('loading of {} caused error:\n{}'.format(fullpath, sys.exc_info()))

    elif sys.version_info >= (3,5):
        # python 3.5+
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(modname, fullpath)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)    
        except:
            mod = None
            raise Exception('loading of {} caused error:\n{}'.format(fullpath, sys.exc_info()))
    else:
        raise Exception ('This version of python is not supported\nUse latest 2.7, 3.3 or newer')

    return mod
