# block definition
# name = 'time_delay'
# libname = 'common'

from spycelib import const

tooltip='''time_delay
parametrized delay
------------------
    inv:        invert every other output
    unit_delay: delay of each cell, can be either float or vector
'''

inp = [(u'a', -60, 0)]
outp = [(u'z0', 60, 0)]
# io   = []

bbox = None

parameters = {'n':(1, dict(min=1)), 'inv':[0,[0,1]]} # pcell if not empty
properties = {'unit_delay':1e-12} # netlist properties

def ports(param):
    n, _ = param['n'] if 'n' in param else (1,dict())
    inv  = param['inv'][0] if 'inv' in param else 0 
    w2 = 50
    inp, outp, inout = [], [], []

    # inp
    inp.append(('a',-w2,0))

    # outp
    for ix in range(n):
        if inv and ix % 2 == 0:
            z ='zn'
        else:
            z = 'z'
        if n > 1:
            z += '{}'.format(ix)
        outp.append((z, w2, ix * const.PD))
    return inp, outp, inout

def getSymbol(param, properties,parent=None,scene=None,):
    import spycelib
    from  Qt import QtGui, QtWidgets, QtCore # see https://github.com/mottosso/Qt.py
    inv        = param['inv'][0] if 'inv' in param else 0 
    attributes = dict()
    attributes['name'] = name
    attributes['libname'] = libname
    inp, outp, _ = ports(param)
    attributes['input'] = inp
    attributes['output'] = outp
    _, left, top     = inp[0]
    _, right, bottom = outp[-1]
    pw = spycelib.const.PW
    d  = 8 # size of circle
    w, h = right-left, bottom-top + 20
    if h < spycelib.const.BHmin:
        dh = spycelib.const.BHmin - h
    else:
        dh = 0
#    print (left+pw/2.0, top-10-dh/2.0, w-pw, h+dh)
    attributes['bbox'] = (left, top-10-dh/2.0, w-d, h+dh)
    b = spycelib.block.Block(attributes,param,properties, name, libname, parent, scene)

    # add circles for inverted outputs, and wires for non-inverted outputs
    pi = QtWidgets.QGraphicsPathItem(b)
    pi.setPen(QtGui.QPen(spycelib.const.colors['block']))
    pp = QtGui.QPainterPath()
    
    for n,x,y in outp:
        if n.startswith('zn'):
            pp.addEllipse(x - pw/2.0 - d, y - d/2.0, d, d)
        else:
            pp.moveTo(x-pw/2.0,   y)
            pp.lineTo(x-pw/2.0-d, y)

    pi.setPath(pp)
    pi.setPos(-b.center)

                 
    return b

def toMyhdlInstance(instname, connectdict, param):
    # properties end up in the connectdict
    inv        = param['inv'][0] if 'inv' in param else 0 
    unit_delay = connectdict['unit_delay'] if 'unit_delay' in connectdict else 1e-12
    try:
        unit_delay = float(unit_delay)
        unit_delay_isfloat = True
    except ValueError:
        unit_delay_isfloat = False

    inp, outp, _ = ports(param)
    
    na, ta = connectdict['a']
    body = ['    @instance']
    body.append('def {}():'.format(instname))
    body.append('    while True:'.format(na))
    body.append('        yield({})'.format(na))
    
    cur = na
    for ix, (z, _, _) in enumerate(outp):
        nz, tz = connectdict[z]
#        print('debug timedelay', unit_delay, type(unit_delay))
        if len(outp) > 1 and not unit_delay_isfloat:
            body.append(    '        yield(delay(int(TIME_UNIT*{}[{}])))'.format(unit_delay, ix))
        else:
            body.append(    '        yield(delay(int(TIME_UNIT*{})))'.format(unit_delay))

        if inv:
            body.append('        {}.next = not {}'.format(nz, cur))
        else:
            body.append('        {}.next = {}'.format(nz, cur))
        cur = nz
    return '\n    '.join(body) + '\n'
    
    

#view variables:
views = {u'icon': None}
