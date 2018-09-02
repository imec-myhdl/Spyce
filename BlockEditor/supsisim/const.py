import os

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
if not os.path.isdir(respath):
    raise Exception('resource path ({}) not found'.format(respath))

pycmd = 'ipython3 qtconsole &'
pyrun = 'python'
TEMP = '.'

# named pins configuration
qtpinlabels  = True # if set to true named ports will get a pinlabel
svgpinlabels = True  # if set to true named ports generate a pinlabel when creating an icon



projectname = 'placeholder'
copyrightText = 'placeholder'
copyrightPolicy = 'placeholder'

# view editors:

viewEditors = [dict(type='verilog', editor='gedit', extension='verilog.v'),
                   dict(type='vhdl', editor='gedit', extension='vhdl.v'),
                   dict(type='doc', editor='libreoffice --writer', extension='doc.odt'),
                   dict(type='python', editor='spyder3', extension='python.py'),
                   dict(type='text', editor='gedit', extension='text.txt'),
                   dict(type='systemverilog', editor='gedit', extension='systemverilog.sv'),
                   dict(type='myhdl', editor='gedit', extension='myhdl.py')]