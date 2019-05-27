# cell definition
# name = 'Register'
# libname = 'common'

from  supsisim import const

tooltip = '''Register (clocked process)

parameters:
-----------
    clk_edge:    any of  ('pos', 'neg'), 
    reset:       any of 'neg, async' # negative active, asynchronous,
                        'pos, async' # positive active, asynchronous, 
                        'neg, sync'  # negative active, synchronous, 
                        'pos, sync'  # positive active, synchronous, 
                        'None'       # no reset
    channels:    number of channels (different signals),
    inv:         invert outputs; any one of ('none', 'odd', 'even', 'all')

properties:
-----------
    delay:       Time delay [s] (from clk to out)
    reset_val    reset value or list of space separated reset values. 
                 the last entry is repeated when channels is higher than lenght of list
    '''


inp = 2
outp = 1

parameters = dict(clk_edge = ('pos', ['pos', 'neg']), 
                  reset = ('neg, async', ['neg, async', 
                                         'pos, async', 
                                         'neg, sync', 
                                         'pos, sync', 
                                         'None']),
                  channels = 1,
                  inv = ['none',('none', 'odd', 'even', 'all')])
properties = {'delay':0.0, 'reset_val':'0'} # for netlisting
#view variables:

def ports(param):
    clk_edge = param['clk_edge'][0] if 'clk_edge' in param else 'pos'
    reset = param['reset'][0] if 'reset' in param else 'neg, async'
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
    if clk_edge == 'pos':
        inp.append(('c', -w2, y)  )
    else:
        inp.append(('cn', -w2, y)  )  
    y += const.PD
    
    rst = ''
    if reset == 'pos, async':
        rst = 'arst'
    elif reset == 'neg, async':
        rst = 'arst_n'
    elif reset == 'pos, sync':
        rst = 'rst'
    elif reset == 'neg, sync':
        rst = 'rst_n'
    if rst:
        inp.append((rst, -w2, y))
    
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
    pi.setPen(supsisim.const.colors['block'])
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
    clk_edge = param['clk_edge'][0] if 'clk_edge' in param else 'pos'
    reset = param['reset'][0] if 'reset' in param else 'neg, async'
    channels =  param['channels'] if 'channels' in param else 1

    # properties are stores in the connectdict
    reset_val = connectdict['reset_val'].split() if 'reset_val' in connectdict else ['0']
    if len(reset_val) < channels:
        reset_val += reset_val[-1] * (channels - len(reset_val)) # repeat last value
    delay = connectdict['delay'] if 'delay' in connectdict else 0.0
    inp, outp, _ = ports(param)

    if clk_edge == 'pos':
        c, ctp = connectdict['c'] # clock
    else:
        c, ctp = connectdict['cn'] # clock not
        
    if reset not in ['None', None]:
        r, rtp = connectdict[inp[-1][0]] # reset
        r_pol, r_sync = reset.split(', ')
        r_pol = 0 if r_pol == 'neg' else 1
    else:
        r = None
        r_pol, r_sync = None, None
    
    indent = '\n        '
    sens   = '{clock}.{pos}edge'.format(clock=c, pos=clk_edge)
    if delay > 0:
        #need @instance decorator, as delay is not allowed in @always
        if reset not in ['None', None]:
            template = ['@instance',
                        'def u_{inst}():',
                        '    while True:',
                        '        yield {sens} # reset = {reset}',
                        '        {sample}',
                        '        yield delay(int({delay}*TIME_UNIT))',
                        '        if {r} == {rpol}:',
                        '            {assign0}',
                        '        else:',
                        '            {assign}']
                    
            indent += '        '
            if r_sync == 'async':
                sens +=', {}.{}edge'.format(r, 'pos' if r_pol else 'neg')
        else:
            template = ['@instance',
                        'def u_{inst}():',
                        '    while True:',
                        '        yield {sens} # reset = {reset}',
                        '        {sample}',
                        '        yield delay(int({delay}*TIME_UNIT))',
                        '        {assign}']
            indent += '    '
    else:
        if reset not in ['None', None]:
            template = ['@always({sens}) # reset = {reset}',
                        'def u_{inst}():',
                        '    if {r} == {rpol}:',
                        '        {assign0}',
                        '    else:',
                        '        {assign}']
            indent += '    '
            if r_sync == 'async':
                sens +=', {}.{}edge'.format(r, 'pos' if r_pol else 'neg')
        else:
            template = ['@always({sens}) # reset = {reset}',
                        'def u_{inst}():',
                        '    {assign}']
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
            assign0.append('{}.next = not {}'.format(nq, reset_val[ix]))
        else:
            assign.append( '{}.next = {}'.format(nq, ndd))
            assign0.append('{}.next = {}'.format(nq, reset_val[ix]))
            
    
    sample   = indent[:-4].join(sample)
    assign0  = indent.join(assign0)
    assign   = indent.join(assign )
    
    return fmt.format(sens=sens, reset=reset, r=r , rpol= r_pol, inst=instname, 
                      assign0=assign0, assign=assign, delay=delay, sample=sample)

views = {}
