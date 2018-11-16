# cell definition
# name = 'Const'
# libname = 'common'

inp = 0
outp = 1

parameters = {} #parametriseerbare cell
properties = dict(const='1') #voor netlisten

def getSymbol(param, properties=dict(), parent=None,scene=None,):
    from  supsisim import block, text
    from  Qt import QtGui, QtCore
    c = properties['const'] if 'const' in properties else '1'
    attributes = dict()
    attributes['name'] = name
    attributes['libname'] = libname
    attributes['input'] = 0
    attributes['output'] = 1
    b = block.Block(attributes,param, properties, name, libname, parent, scene)

    # replace rect
    port = b.ports()[0] 
    path = QtGui.QPainterPath()
    path.moveTo(port.pos())
    path.lineTo(port.pos() + QtCore.QPointF(-20, 0))
    b.setPath(path)
    
    # hide label
    b.label.hide()
    # create a new label in the centre
    tt = '{}'.format(c)
    ll = text.textItem(tt, anchor=6, parent=b)
    ll.setPos(port.pos() + QtCore.QPointF(-20, 0))
    ll.setMutable(False)
    
    return b
    
def toMyhdlInstance(instname, connectdict, param):
    # properties end up in the connectdict
    c = connectdict['const'] if 'const' in connectdict else '1'
    z = connectdict['.o_0']


    fmt = '    @always_comb\n' + \
          '    def u_{}():\n' + \
          '        {}.next = {}\n'
    return fmt.format(instname, z, c)

views = {}
