import os, sys
from collections import OrderedDict


GRID = 10
PW   = 8   # pin width
PD   = 20  # pin distance (spacing between pins in blocks)
NW   = 4   # node width
LW   = 1.5 # line width for conncetion

BWmin = 80 # block minimum width
BHmin = 60 # block minimum height


DB = 2   # selection radius (dynamically scaling whith zoom)

stdfont = 'Sans Serif,12' # used for (pin)labels/comments

if 'PYSUPSICTRL' in os.environ:
    path = os.environ['PYSUPSICTRL']
else:
    print('Environment variable PYSUPSICTRL is not set.')
    path = os.getcwd()
    if path.endswith('supsisim'):
        path = os.path.dirname(path)
    print('defaulting to {}'.format(path))
#    sys.exit()
    
# defaults for icon creation
# icons use QFont("Helvetica", 14, QFont.Normal) 
icon_font_size = 10  # height
icon_pin_size  = 10 # length of line segment (starting at pin-position)
icon_cache_dir = '.iconcache'
netlist_dir    = 'netlist' #path for netlists
    
# path to resources
respath = os.path.join(path, 'resources')
if not os.path.isdir(respath):
    raise Exception('resource path ({}) not found'.format(respath))

pycmd = 'ipython3 qtconsole &'
pyrun = 'python'

# used in netlist
projectname     = 'placeholder'
copyrightText   = 'placeholder'
copyrightPolicy = 'placeholder'


celltemplate = """# cell definition
# name = '{name}'
# libname = '{libname}'

inp  = {inp}
outp = {outp}
io   = {io}
bbox = {bbox}

parameters = {parameters} # pcell if not empty
properties = {properties} # netlist properties

#view variables:
views = {views}
"""

#==============================================================================
# predefined colors
# Qt.white       3  White (#ffffff)
# Qt.black       2  Black (#000000)
# Qt.red         7  Red (#ff0000)
# Qt.darkRed     13 Dark red (#800000)
# Qt.green       8  Green (#00ff00)
# Qt.darkGreen   14 Dark green (#008000)
# Qt.blue        9  Blue (#0000ff)
# Qt.darkBlue    15 Dark blue (#000080)
# Qt.cyan        10 Cyan (#00ffff)
# Qt.darkCyan    16 Dark cyan (#008080)
# Qt.magenta     11 Magenta (#ff00ff)
# Qt.darkMagenta 17 Dark magenta (#800080)
# Qt.yellow      12 Yellow (#ffff00)
# Qt.darkYellow  18 Dark yellow (#808000)
# Qt.gray        5  Gray (#a0a0a4)
# Qt.darkGray    4  Dark gray (#808080)
# Qt.lightGray   6  Light gray (#c0c0c0)
#==============================================================================
colors = dict() 
if 'Qt'in sys.modules: # needed to import without gui
    from Qt.QtCore import Qt
#                           (line,        fill)
    colors['port_input']  = (Qt.black,    Qt.black)
    colors['port_output'] = (Qt.black,    Qt.black)
    colors['port_inout']  = (Qt.black,    Qt.black)
    colors['port_ipin']   = (Qt.black,    Qt.darkRed)
    colors['port_opin']   = (Qt.black,    Qt.darkRed)
    colors['port_iopin']  = (Qt.black,    Qt.darkRed)
    colors['node']        = (Qt.darkBlue, Qt.darkBlue)
    colors['block']       =  Qt.darkGreen # no fill color
    colors['connection']  =  Qt.darkBlue  # no fill color
    colors['comment']     =  Qt.darkGray  # no fill color
    colors['signalType']  =  Qt.darkGray  # no fill color


#==============================================================================
# view editors:
textEditor        = 'kate'
codeEditor        = 'kate'
officeEditor      = 'libreoffice --writer'
pythonEditor      = 'spyder3'

viewTypes    = OrderedDict()
#               (viewtype         editor          extension   )
viewTypes['diagram']       = (pythonEditor,  '.diagram.py')
viewTypes['myhdl']         = (pythonEditor,  '.myhdl.py'  )
viewTypes['blk_source']    = (pythonEditor,  '.py'        )
viewTypes['text']          = (textEditor,    '.txt'       )
viewTypes['vhdl']          = (codeEditor,    '.vhd'       )
viewTypes['systemverilog'] = (codeEditor,    '.sv'        )
viewTypes['verilog']       = (codeEditor,    '.v'         )
viewTypes['doc']           = (officeEditor,  '.odt'       )
#==============================================================================
