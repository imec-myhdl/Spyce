# cell definition
# name = 'Sum'
# libname = 'common'
from  spycelib import const

inp = 2
outp = 1

parameters = dict(A = '++')
properties = {'name': 'sumBlk'} #voor netlisten
#view variables:

def ports(param):
   polarities = param['A'] if 'A' in param else '++'
   inp, outp, inout = [], [], []
   spacing = 2*const.PD if len(polarities) <= 2 else const.PD
   w2 = 40
   for ix in range(len(polarities)):
       inp.append(('.a{}'.format(ix), -w2, ix*spacing))
   yy = int(spacing*(len(polarities)-1)/2/const.GRID)*const.GRID
   outp.append(('.z', w2, yy))
   return inp, outp, inout



def getSymbol(param, properties,parent=None,scene=None):
    import spycelib.block
    from  Qt import QtGui, QtWidgets, QtCore # see https://github.com/mottosso/Qt.py
    polarities = param['A'] if 'A' in param else '++'
    inp, outp, inout = ports(param)    
    
    attributes = dict()
    attributes['name'] = name
    attributes['libname'] = libname
    attributes['input'] = inp
    attributes['output'] = outp
    b = spycelib.block.Block(attributes,param,properties, name, libname, parent, scene)
    
    # create a new pathitem with a plus and circle
    pi = QtWidgets.QGraphicsPathItem(b)
    pi.setPen(QtGui.QPen(QtCore.Qt.black))
    pp = QtGui.QPainterPath()
    # draw plus
    pp.moveTo(-11,0)
    pp.lineTo(11, 0)
    pp.moveTo(0, -11)
    pp.lineTo(0, 11)
    #draw circle
    pp.addEllipse(-15, -15, 30, 30)
    pi.setPath(pp)
    pi.setPos(5,0) # move a little to the right for optical reasons
    
    # add + or - signs to ports
    for port in b.ports():
        portname = port.label.text()
        if portname.startswith('.a'):
            sign = polarities[int(portname[2:])]
            port.p.moveTo(10, 0)
            port.p.lineTo(20, 0)
            if sign == '+':
                port.p.moveTo(15, -5)
                port.p.lineTo(15, 5)
            port.setPath(port.p)
            
    return b
    
def toMyhdlInstance(instname, connectdict, param):
    # properties end up in the connectdict
    polarities = param['A'] if 'A' in param else '++' 
    inputs = []
    z, zp = connectdict['.z']

    shift = dict()
    for c in connectdict:
        if c.startswith('.a'):
            net,tp = connectdict[c]
            shift[net] = 0
            tp = tp.strip()
            if tp.strip().startswith('Signal'):
                tp = tp[6:].strip('() ')
            if tp.startswith('fixbv'):
                tp = tp[5:].strip('() ')
                a, _, b = tp.partition('shift')
                if b:
                    s = int(b.lstrip(' =').split(',')[0])
                else:
                    s = int(tp.split(',')[1])
                shift[net] = s
    target_shift = min(shift.values())
    
    for ix, s in enumerate(polarities):
        net,tp = connectdict['.a{}'.format(ix)]
        ds = shift[net] - target_shift
        shnet = '({}<<{})'.format(net, ds) if ds else net
        if s == '-':
            if str(net).isalnum() or shnet != net:
                inputs.append('- {}'.format(shnet))
            else:
                 inputs.append('- ({})'.format(shnet))
        else:
            inputs.append('+ {}'.format(shnet))

    expr = ' '.join(inputs).lstrip('+ ')

    if '{' in z: # inline expression
        d = dict()
        d[z] = expr
        return dict(__expr__ = d)
    else:
        fmt = '    @always_comb\n' + \
              '    def u_{}():\n' + \
              '        {}.next = {}\n'
        return fmt.format(instname, z, expr)
        

views = {}
