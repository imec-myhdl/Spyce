# block definition
# name = 'defines'
# libname = 'common'

tooltip = '''Use this block to define constants for use in the rest of the diagram

each entry should be a python line (without trailing newline)
Be aware that the equation must also be valid systemVerilog when netlisting to verilog

Note: property names are ignored, but determine execution order (alphabetic)'''

inp  = []
outp = []
# io   = []

bbox = None

parameters = {} # pcell if not empty
properties = {} # netlist properties

def getSymbol(param, properties,parent=None,scene=None,):
    from  spycelib import block, text
    attributes = dict()
    attributes['name'] = name
    attributes['libname'] = libname
    attributes['input'] = []
    attributes['output'] = []
#    attributes['icon'] = views['icon']
    b = block.Block(attributes,param,properties, name, libname, parent, scene)
    # display properties
    t = []
    for k in sorted(properties.keys()):
        v = properties[k]
        t.append('{}'.format(v))
    if len(t) == 0:
        t = ['example: pi = 3.1415']
    lbl = text.textItem('\n'.join(t), anchor=7, parent=b)
    lbl.setMutable(False)
    width = lbl.boundingRect().width()
    height = lbl.boundingRect().height()
    w = max(int(width/20)*20 + 20, 40)
    h = max(int(height/20)*20 + 20, 40)
    b.bbox = [-w//2, -h//2, w, h]
    b.setup()
    x, y = b.center.x(), b.center.y()
    lbl.setPos(-w//2, -h//2)
        
    return b


def toMyhdlInstance(instname, connectdict, param):
    r = ['    # {}'.format(instname)]
    for key in sorted(connectdict.keys()): # only properties, as there are no connections
        r.append('    {}'.format(connectdict[key]))
    
    d = dict()    
    d['__defs__'] = '\n'.join(r)
    return d

#view variables:
views = {u'icon': None}
