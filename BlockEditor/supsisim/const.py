import os, sys

GRID = 10
PW   = 8   # pin width
PD   = 40  # pin distance (spacing)

BWmin = 80 # block minimum width
BHmin = 60 # block minimum height

NW = 2
LW =1.5

DB = 0.5
if 'PYSUPSICTRL' in os.environ:
    path = os.environ['PYSUPSICTRL']
else:
    print('Environment variable PYSUPSICTRL is not set, exiting...')
    sys.exit()

respath = os.path.join(path, 'resources')

pycmd = 'ipython3 qtconsole &'
pyrun = 'python'
TEMP = '.'

