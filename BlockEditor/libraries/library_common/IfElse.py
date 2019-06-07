# cell definition
# name = 'IfElse'
# libname = 'common'

tooltip = '''
IfElse
---
parameters:
    n_if_inp:  number of inputs for if_condition  
    ifcond:    (comma separated) list of boolean equations
    channels:  number of channels (different signals)

example ifcond: '{i0} == 1, {i1} > {i0}'
'''

inp = 2
outp = 1

parameters = dict(n_if_inp=1, ifcond='{i0} == 1', channels=1)
properties = {} #voor netlisten

from  supsisim import const

def ports(param):
    '''return inputs, outputs and inouts'''
    n_if_inp = param['n_if_inp'] if 'n_if_inp' in param else 1
    ifcond =  param['ifcond'] if 'ifcond' in param else '{i0} == 1'
    ncond = len(ifcond.split(','))
    channels = param['channels'] if 'channels' in param else 1
    

    w2, y = 100, 0
    inp = []
    outp = []
    for i in range(n_if_inp):
        inp.append(('i{}'.format(i), -w2, y))
        y += const.PD
    y += const.PD # * (2 + ncond)
    for i in range(channels):
        for c in range(ncond+1):
            inp.append(('.if{}_{}'.format(i, c), -w2, y))
            if c == ncond:
                 outp.append(('.z{}'.format(i), w2, y))
            y += const.PD
        y += const.PD
                    
    inout = []
    return inp, outp, inout

def getSymbol(param, properties, parent=None, scene=None,):
    from  supsisim import block, text
    ifcond =  param['ifcond'] if 'ifcond' in param else '{i0} == 1'
    ifcond = [i.strip() for i in ifcond.split(',')]
    ncond = len(ifcond)
    
    attributes = dict()
    attributes['name'] = name
    attributes['libname'] = libname
    inp, outp, _ = ports(param)
    attributes['input'] = inp
    attributes['output'] = outp
    attributes['icon'] = views['icon']
    b = block.Block(attributes,param,properties, name, libname, parent, scene)
    for p in b.ports():
        t = p.label.text()
        if t.startswith('.if'):
            c = int(t.split('_')[-1])
            tt = 'if' if c == 0 else 'else' if c == ncond else 'elif'
            if tt.endswith('if'):
                tt += ' {}'.format(ifcond[c])
            l = text.textItem(tt, anchor=4, parent=b)
            x, y = p.pos().x(), p.pos().y()
            l.setPos(x+5,y)
            l.setMutable(False)
#        elif t.startswith('i'):
#            i = int(t[1:])
#            if i == ncond - 1:
#                tt = []
#                for ix, cc in enumerate(ifcond):
#                    tt.append('{}: {}'.format(ix, cc))
#                tt.append('{}: otherwise'.format(ncond))
#                l = text.textItem('\n'.join(tt), anchor=7, parent=b)
#                x, y = p.pos().x(), p.pos().y()
#                l.setPos(x+5,y+5)
#                l.setMutable(False)
               
                
    return b
    
def toMyhdlInstance(instname, connectdict, param):
    # properties end up in the connectdict
    n_if_inp = param['n_if_inp'] if 'n_if_inp' in param else 1
    ifcond =  param['ifcond'] if 'ifcond' in param else '{i0} == 1'
    cond = [s.strip() for s in ifcond.split(',')]
    ncond = len(cond)
    channels = param['channels'] if 'channels' in param else 1

    inp, outp, _ = ports(param)
    dd = dict()
    for i in range(n_if_inp):
        nm = 'i{}'.format(i)
        dd[nm], _ = connectdict[nm] # store name in dict

    r =          '    @always_comb\n' 
    r +=         '    def u_{inst}():\n'.format(inst=instname)
    for c in range(ncond+1): 
        if c == 0:
            r += '        if {}:\n'.format(cond[c].format(**dd))
        elif c == ncond:
            r += '        else:\n'
        else:
            r += '        elif {}:\n'.format(cond[c].format(**dd))
        for i in range(channels):
            a, tpa = connectdict['.if{}_{}'.format(i, c)]
            z, tpz = connectdict['.z{}'.format(i)]
            if '{' not in z:
                r += '            {}.next = {}\n'.format(z, a)

    ex = []
    d = dict()
    for i in range(channels):
        z, tpz = connectdict['.z{}'.format(i)]
        if '{' in z: # inline expression
            for c in range(ncond+1): 
                a, tpa = connectdict['.if{}_{}'.format(i, c)]
                if c == 0:
                    print ('ifelse debug 4')
                    ex.append('{} if {}'.format(a, cond[c].format(**dd)))
                    print ('ifelse debug 5')
                elif c == ncond:
                    ex.append('else {}'.format(a))
                else:
                    ex.append('{} else if {}'.format(a, cond[c].format(**dd)))
            d[z] = ' '.join(ex)
    print (d)
    if d:
        if '.next' in r:
            return dict(__expr__ = d, __main__ = r)
        else:
            return dict(__expr__ = d)
    else:
        return r

views = {}
