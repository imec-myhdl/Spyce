# block definition
# name = 'Bitwise' Bitwise operation
# libname = 'math'

inp  = []
outp = []
# io   = []

bbox = None

parameters = {'A':'++','Z':'+'} # pcell if not empty
properties = {'delay':0.0, 'op':['&', '& | ^ ~ << >>'.split()]} # netlist properties

def ports(param):
   from spycelib import const
   A = param['A'] if 'A' in param else '++'
   Z = param['Z'] if 'Z' in param else '+'
   inp, outp, inout = [], [], []
   spacing = 2*const.PD if len(A) <= 2 else const.PD
   w2 = 40
   for ix, s in enumerate(A):
       if s == '+':
           inp.append(('.a{}'.format(ix), -w2, ix*spacing))
       else:
           inp.append(('.an{}'.format(ix), -w2, ix*spacing))
    
   yy = int(spacing*(len(A)-1)/2/const.GRID)*const.GRID
   if Z.startswith('+'):
       outp.append(('.z', w2, yy))
   else:
       outp.append(('.zn', w2, yy))
       
   return inp, outp, inout
   
def getSymbol(param, properties,parent=None,scene=None):
    global name, libname
    from spycelib import block, const, text
    from  Qt import QtGui, QtWidgets, QtCore # see https://github.com/mottosso/Qt.py
    A = param['A'] if 'A' in param else '++'
    Z = param['Z'] if 'Z' in param else '+'
    operator = properties['op'][0] if 'op' in properties else '&'
    inp, outp, inout = ports(param)    
    
    _, left, top = inp[0]
    bottom       = inp[-1][2]
    right        = outp[0][1]
    pw = const.PW
    d  = 8 # size of circle
    w, h = right-left, bottom-top + 20
#    if h < const.BHmin:
#        dh = const.BHmin - h
#    else:
#        dh = 0
    dh = 0
    attributes = dict()
    _name = properties.pop('_name') if '_name' in properties else name
    _libname = properties.pop('_libname') if '_libname' in properties else libname

    attributes['name']    = _name
    attributes['libname'] = _libname
    attributes['input']   = inp
    attributes['output']  = outp
    attributes['bbox']    = (left+d, top-10-dh/2.0, w-2*d, h+dh)
    attributes['icon']    = views['icon']

    b = block.Block(attributes,param,properties, _name, _libname, parent, scene)
    # add circles for inverted outputs, and wires for non-inverted outputs
    pi = QtWidgets.QGraphicsPathItem(b)
    pi.setPen(QtGui.QPen(const.colors['block']))
    pp = QtGui.QPainterPath()
    
    for n,x,y in outp:
        if n.startswith('.zn'):
            pp.addEllipse(x - pw/2.0 - d, y - d/2.0, d, d)
        else:
            pp.moveTo(x-pw/2.0,   y)
            pp.lineTo(x-pw/2.0-d, y)

    for n,x,y in inp:
        if n.startswith('.an'):
            pp.addEllipse(x + pw/2.0, y - d/2.0, d, d)
        else:
            pp.moveTo(x+pw/2.0,   y)
            pp.lineTo(x+pw/2.0+d, y)

    pi.setPath(pp)
    pi.setPos(-b.center)

    # create a new label in the centre
    ll = text.textItem('{}'.format(operator), anchor=5, parent=b)
    font = ll.font()
    font.fromString('Sans Serif,16')
    ll.setFont(font)
#    ll.setPos(0,0)
    ll.setMutable(False)
            
    return b
    
def toMyhdlInstance(instname, connectdict, param):
    # properties end up in the connectdict
    A = param['A'] if 'A' in param else '++'
    Z = param['Z'] if 'Z' in param else '+'
    operator = connectdict['op'][0] if 'op' in connectdict else '&'
    delay    = connectdict['delay'] if 'delay' in connectdict else 0.0
    inp, outp, inout = ports(param)    
    inputs = []
    sens = []
    z, x, y = outp[0]
    out, tp = connectdict[z]
    for n, x, y in inp:
        net,tp = connectdict[n]
        sens.append(net)
        if n.startswith('.an'):
            inputs.append('(not {})'.format(net))
        else:
            inputs.append('({})'.format(net))

    opp  = ' ' + operator + ' '
    expr = opp.join(inputs)
    if z.startswith('.zn'):
        expr = 'not ({})'.format(expr)
    
    if delay > 0.0:
        t  = ['@instance',
              'def u_{inst}():',
              '    while True:',
              '        yield {sens}',
              '        yield(delay(int({delay}*TIME_UNIT)))',
              '        {out}.next = {expr}']
    elif '{' in out:
        d = dict()
        d[out] = expr
        return dict(__expr__ = d)
    else:
        t  = ['@always_comb',
              'def u_{inst}():',
              '    {out}.next = {expr}']
    fmt = '    ' + '\n    '.join(t) + '\n'
    return fmt.format(inst=instname, out=out, expr=expr, sens=', '.join(sens), delay=delay)


#view variables:
views = {u'icon': None}
