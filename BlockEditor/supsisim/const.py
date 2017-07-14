import os, sys

GRID = 10
PW   = 8   # pin width
PD   = 40  # pin distance (spacing)

BWmin = 80 # block minimum width
BHmin = 60 # block minimum height

NW = 2     # node width
LW =1.5    # line width

DB = 0.5   # selection radius for block (connection has 4 times bigger radius)
if 'PYSUPSICTRL' in os.environ:
    path = os.environ['PYSUPSICTRL']
else:
    print('Environment variable PYSUPSICTRL is not set.')
    path = os.getcwd()
    print('defaulting to {}'.format(path))
#    sys.exit()
    
    
# path to resources
respath = os.path.join(path, 'resources')

pycmd = 'ipython3 qtconsole &'
pyrun = 'python'
TEMP = '.'

