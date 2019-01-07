# cell definition
# name = 'Sum'
# libname = 'common'
from  supsisim import const

inp = 2
outp = 1

parameters = dict(A = '++')
properties = {'name': 'sumBlk'} #voor netlisten
#view variables:

def ports(param):
   gains = param['A'] if 'A' in param else '++'
   inp, outp, inout = [], [], []
   spacing = 2*const.PD if len(gains) <= 2 else const.PD
   w2 = 40
   for ix in range(len(gains)):
       inp.append(('.a{}'.format(ix), -w2, ix*spacing))
   yy = int(spacing*(len(gains)-1)/2/const.GRID)*const.GRID
   outp.append(('.z', w2, yy))
   return inp, outp, inout



def getSymbol(param, properties,parent=None,scene=None):
    import supsisim.block
    from  Qt import QtGui, QtWidgets, QtCore # see https://github.com/mottosso/Qt.py
    gains = param['A'] if 'A' in param else '++'
    inp, outp, inout = ports(param)    
    
    attributes = dict()
    attributes['name'] = name
    attributes['libname'] = libname
    attributes['input'] = inp
    attributes['output'] = outp
    b = supsisim.block.Block(attributes,param,properties, name, libname, parent, scene)
    
    # create a new pathitem with a plus and citcle
    pi = QtWidgets.QGraphicsPathItem(b)
    pi.setPen(QtCore.Qt.black)
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
            sign = gains[int(portname[2:])]
            port.p.moveTo(10, 0)
            port.p.lineTo(20, 0)
            if sign == '+':
                port.p.moveTo(15, -5)
                port.p.lineTo(15, 5)
            port.setPath(port.p)
            
    return b
    
def toMyhdlInstance(instname, connectdict, param):
    # properties end up in the connectdict
    gains = param['A'] if 'A' in param else '++' 
    inputs = []
    outp, tp = connectdict['.z']
    for ix, s in enumerate(gains):
        net,tp = connectdict['.a{}'.format(ix)]
        if s == '-':
            inputs.append('- {}'.format(net))
        else:
            inputs.append('+ {}'.format(net))

    expr = ' '.join(inputs).lstrip('+ ')
    fmt = '    @always_comb\n' + \
          '    def u_{}():\n' + \
          '        {}.next = {}\n'
    return fmt.format(instname, outp, expr)

views = {}
