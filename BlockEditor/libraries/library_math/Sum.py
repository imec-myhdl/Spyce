# cell definition
# name = 'Sum'
# libname = 'common'

inp = 2
outp = 1

parameters = dict(A = '++')
properties = {'name': 'sumBlk'} #voor netlisten
#view variables:




def getSymbol(param, properties,parent=None,scene=None,):
    import supsisim.block
    from  Qt import QtGui, QtWidgets, QtCore # see https://github.com/mottosso/Qt.py
    gains = param['A'] if 'A' in param else '++'
    attributes = dict()
    attributes['name'] = name
    attributes['libname'] = libname
    attributes['input'] = len(gains) if 'A' in param else inp
    attributes['output'] = 1
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
        if portname.startswith('.i_'):
            sign = gains[int(portname[3:])]
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
    outp = connectdict['.o_0']
    for ix, s in enumerate(gains):
        net = connectdict['.i_{}'.format(ix)]
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
