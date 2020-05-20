# block definition
# name = 'Concat'
# libname = 'common'

from supsisim import const

tooltip = '''Returns an intbv object formed by concatenating the arguments.
The following argument types are supported (All these objects have a defined bit width.): 
     intbv objects with a defined bit width, 
     bool objects 
     bit strings 

The first argument 'base' is special as it does not need to have a defined bit width. 
In addition to these typeas also unsized intbv and int/long are allowed for base
'''

inp = [(u'a0', -60, 0)]
outp = [(u'z', 60, 0)]
# io   = []

bbox = None

parameters = {'n':   (1, dict(min=1)),
              'inv': ['none',('none', 'odd', 'even', 'all')]} # pcell if not empty
              
properties = {'a0_to':['lsb',['lsb','msb']]} # netlist properties

def ports(param):
    inv = param['inv'][0] if 'inv' in param else 'none'
    n, _ = param['n'] if 'n' in param else (1,dict())
    w2 = 50
    inp, outp, inout = [], [], []

    # outp
    outp.append(('z',w2,0))

    # inp
    for ix in range(n):
                
        if inv == 'all':
             a = 'an'           
        elif (ix % 2) == 1 and inv == 'odd':
            a = 'an'
        elif (ix % 2) == 0 and inv == 'even':
            a = 'an'
        else:
            a = 'a'
        if n >1: 
            a += '{}'.format(ix)
        inp.append((a, -w2, ix * const.PD))
        
    return inp, outp, inout

def getSymbol(param, properties,parent=None,scene=None,):
    import supsisim
    from  Qt import QtGui, QtWidgets, QtCore # see https://github.com/mottosso/Qt.py
    attributes = dict()
    attributes['name'] = name
    attributes['libname'] = libname
    inp, outp, _ = ports(param)
    attributes['input'] = inp
    attributes['output'] = outp
    _, left, bottom     = inp[-1]
    _, right, top = outp[0]
    pw = supsisim.const.PW
    d  = 8 # size of circle
    w, h = right-left, bottom-top + 20
    if h < supsisim.const.BHmin:
        dh = supsisim.const.BHmin - h
    else:
        dh = 0
#    print (left+pw/2.0, top-10-dh/2.0, w-pw, h+dh)
    attributes['bbox'] = (left+d, top-10-dh/2.0, w-d, h+dh)
    b = supsisim.block.Block(attributes,param,properties, name, libname, parent, scene)

    # add circles for inverted outputs, and wires for non-inverted outputs
    pi = QtWidgets.QGraphicsPathItem(b)
    pi.setPen(QtGui.QPen(const.colors['block']))
    pp = QtGui.QPainterPath()
    
    for n,x,y in inp:
        if n.startswith('an'):
            pp.addEllipse(x + pw/2.0, y - d/2.0, d, d)
        else:
            pp.moveTo(x+pw/2.0,   y)
            pp.lineTo(x+pw/2.0+d, y)

    pi.setPath(pp)
    pi.setPos(-b.center)
                 
    return b

def toMyhdlInstance(instname, connectdict, param):
    # properties end up in the connectdict
    a0        = connectdict['a0_to'][0] if 'a0_to' in connectdict else 'lsb' 
    inp, outp, _ = ports(param)
    
    nz, tz = connectdict['z']
    body = ['    @always_comb']
    body.append('def {}():'.format(instname))
    
    nets = []
    for (a, _, _) in inp:
        na, ta = connectdict[a]
        if na.startswith('an'):
            nets.append('not '+na)
            
        else:
            nets.append(na)
        
    if a0 == 'lsb':
        body.append('    # a0 to lsb, concat: first argument = msb')
        body.append('    {}.next = concat('.format(nz) + ',\n                '.join(reversed(nets)) + ')')
    else:
        body.append('    # a0 to msb, concat: first argument = msb')
        body.append('    {}.next = concat('.format(nz) + ',\n                '.join(nets) + ')')
    
    return '\n    '.join(body) + '\n'
    
    

#view variables:
views = {u'icon': None}
