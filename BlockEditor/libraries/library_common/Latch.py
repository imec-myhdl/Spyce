# cell definition
# name = 'Latch'
# libname = 'common'

from  supsisim import const

inp = 2
outp = 1

tooltip = '''Latch with optional delay, 
transparent when c = 1 (or cn == 0)''' 

parameters = dict(clk_pol = ('pos', ['pos', 
                                      'neg']), 
                  channels = 1,
                  inv = ['none',('none', 'odd', 'even', 'all')])
properties = {'delay':0.0} #voor netlisten
#view variables:

def ports(param):
    clk_pol = param['clk_pol'][0] if 'clk_pol' in param else 'pos'
    inv = param['inv'][0] if 'inv' in param else 'none'
    channels =  param['channels'] if 'channels' in param else 1
    w2, y = 60, 0
    inp, outp, inout = [], [], []
    for ix in range(channels):
        d = 'd{}'.format(ix) if channels >1 else 'd'
        
        if inv == 'all':
             q = 'qn'           
        elif (ix % 2) == 1 and inv == 'odd':
            q = 'qn'
        elif (ix % 2) == 0 and inv == 'even':
            q = 'qn'
        else:
            q = 'q'
        if channels >1: 
            q += '{}'.format(ix)
            
        inp.append((d, -w2, y))
        outp.append((q, w2, y))
        y += const.PD
            
    y += const.PD
    if clk_pol == 'pos':
        inp.append(('c', -w2, y)  )
    else:
        inp.append(('cn', -w2, y)  )  
    y += const.PD
        
    return inp, outp, inout

def getSymbol(param, properties, parent=None, scene=None,):
    import supsisim
    from  Qt import QtGui, QtWidgets, QtCore # see https://github.com/mottosso/Qt.py
    inp, outp, _ = ports(param)
    attributes = dict()
    attributes['name'] = name
    attributes['libname'] = libname
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
    attributes['bbox'] = (left+d, top-10-dh/2.0, w-2*d, h+dh)
    b = supsisim.block.Block(attributes,param,properties, name, libname, parent, scene)
    # add circles for inverted outputs, and wires for non-inverted outputs
    pi = QtWidgets.QGraphicsPathItem(b)
    pi.setPen(QtGui.QPen(supsisim.const.colors['block']))
    pp = QtGui.QPainterPath()
    
    for n,x,y in outp:
        if n.startswith('qn'):
            pp.addEllipse(x - pw/2.0 - d, y - d/2.0, d, d)
        else:
            pp.moveTo(x-pw/2.0,   y)
            pp.lineTo(x-pw/2.0-d, y)

    for n,x,y in inp:
        if n.endswith('n'):
            pp.addEllipse(x + pw/2.0, y - d/2.0, d, d)
        else:
            pp.moveTo(x+pw/2.0,   y)
            pp.lineTo(x+pw/2.0+d, y)

    pi.setPath(pp)
    pi.setPos(-b.center)
    return b
    
    
    return b
    
def toMyhdlInstance(instname, connectdict, param):
    # properties end up in the connectdict
    clk_pol = param['clk_pol'][0] if 'clk_pol' in param else 'pos'
#    channels =  param['channels'] if 'channels' in param else 1
    delay = connectdict['delay'] if 'delay' in connectdict else 0.0
    inp, outp, _ = ports(param)

    if clk_pol == 'pos':
        c, ctp = connectdict['c'] # clock
        cpol = 1
    else:
        c, ctp = connectdict['cn'] # clock not
        cpol = 0
        
    
    indent = '\n            '
    sens   = [c]
    for n, x, y in inp[:-1]:
        nn,nt = connectdict[n]
        sens.append(nn)
    sens = ', '.join(sens)
        
    if delay > 0:
        #need @instance decorator, as delay is not allowed in @always
        template = ['@instance',
                    'def u_{inst}():',
                    '    while True:',
                    '        yield {sens}',
                    '        if {c} == {cpol}:',
                    '            {sample}',
                    '            yield delay(int({delay}*TIME_UNIT))',
                    '            {assign}']
        indent += '    '
    else:
        template = ['@always({sens})',
                    'def u_{inst}():',
                    '    if {c} == {cpol}:',
                    '        {assign}']
    fmt = '    ' + '\n    '.join(template) + '\n'
    sample = []    
    assign0 = []
    assign  = []
    for ix, (n, x, y) in enumerate(outp):
        nd, ndtp = connectdict[inp[ix][0]]
        nq, nqtp = connectdict[n]
        if delay > 0.0:
            ndd = '_' + nd 
            sample.append('{} = {}'.format(ndd, nd))
        else:
            ndd = nd 
            
        if n.startswith('qn'):
            assign.append( '{}.next = not {}'.format(nq, ndd))
        else:
            assign.append( '{}.next = {}'.format(nq, ndd))
            
    
    sample   = indent[:-4].join(sample)
    assign0  = indent.join(assign0)
    assign   = indent.join(assign )
    
    return fmt.format(sens=sens, c=c, cpol=cpol, inst=instname, 
                      assign=assign, delay=delay, sample=sample)

views = {}
