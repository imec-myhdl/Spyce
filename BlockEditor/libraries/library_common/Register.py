# cell definition
# name = 'Register'
# libname = 'common'

from  supsisim import const

inp = 2
outp = 1

parameters = dict(clk_edge = ('pos', ['pos', 
                                      'neg']), 
                  reset= ('neg, async', ['neg, async', 
                                         'pos, async', 
                                         'neg, sync', 
                                         'pos, sync', 
                                         'None']),
                  channels = 1)
properties = {} #voor netlisten
#view variables:

def ports(param):
    reset = param['reset'][0] if 'reset' in param else 'neg, async'
    channels =  param['channels'] if 'channels' in param else 1
    w2, y = 50, 0
    inp, outp, inout = [], [], []
    for ix in range(channels):
        d = 'd{}'.format(ix) if channels >1 else 'd'
        q = 'q{}'.format(ix) if channels >1 else 'q'
        inp.append((d, -w2, y))
        outp.append((q, w2, y))
        y += const.PD
            
    y += const.PD
    inp.append(('c', -w2, y)  )  
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
    from  supsisim import block, text
    inp, outp, _ = ports(param)
    attributes = dict()
    attributes['name'] = name
    attributes['libname'] = libname
    attributes['input'] = inp
    attributes['output'] = outp
    b = block.Block(attributes,param,properties, name, libname, parent, scene)
    
    
    return b
    
def toMyhdlInstance(instname, connectdict, param):
    # properties end up in the connectdict
    clk_edge = param['clk_edge'][0] if 'clk_edge' in param else 'pos'
    reset = param['reset'][0] if 'reset' in param else 'neg, async'
    channels =  param['channels'] if 'channels' in param else 1
    
    inp, outp, _ = ports(param)

    c, ctp = connectdict['c'] # clock
    if reset:
        r, rtp = connectdict[inp[-1][0]] # reset
        r_pol, r_sync = reset.split(', ')
        r_pol = 0 if r_pol == 'neg' else 1
    else:
        r = None
        r_pol, r_sync = None, None
    
    indent = '\n        '
    sens   = '{clock}.{pos}edge'.format(clock=c, pos=clk_edge)
    if reset:
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
    assign0 = []
    assign  = []
    for ix in range(channels):
        nd, ndtp = connectdict[inp[ix][0]]
        nq, nqtp = connectdict[outp[ix][0]]
        assign.append( '{}.next = {}'.format(nq, nd))
        assign0.append('{}.next = {}'.format(nq, 0))
    assign0  = indent.join(assign0)
    assign   = indent.join(assign )
    
    return fmt.format(sens=sens, reset=reset, r=r , rpol= r_pol, inst=instname, 
                      assign0=assign0, assign=assign)

views = {}
