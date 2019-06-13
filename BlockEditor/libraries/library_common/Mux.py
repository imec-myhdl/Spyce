# cell definition
# name = 'Mux'
# libname = 'common'

tooltip = '''
mux
---
parameter 'sel' is a space separated list of input values for select. 
last entry will encode the default value
'''

inp = 2
outp = 1

parameters = dict(sel='0 1')
properties = {} #voor netlisten

from  supsisim import const

def ports(param):
    '''return inputs, outputs and inouts'''
    if 'sel' in param:
        sel =  [eval(i) for i in param['sel'].split()]
    else:
        sel = [0, 1]
    channels = len(sel)
    w2, y = 50, 0
    inp = []
    for i in range(channels):
        inp.append(('.i{}'.format(i), -w2, y))
        y += const.PD
            
    y += const.PD
    inp.append(('s', -w2, y))
    
    outp = [('z', w2, int(y/const.PD/2-1)*const.PD)]
    inout = []
    return inp, outp, inout

def getSymbol(param, properties, parent=None, scene=None,):
    from  supsisim import block, text
    if 'sel' in param:
        sel =  [eval(i) for i in param['sel'].split()]
    else:
        sel = [0, 1]
    attributes = dict()
    attributes['name'] = name
    attributes['libname'] = libname
    inp, outp, _ = ports(param)
    attributes['input'] = inp
    attributes['output'] = outp
    attributes['icon'] = views['icon']
    b = block.Block(attributes,param,properties, name, libname, parent, scene)
    for p in b.ports():
        if p.porttype == 'input':
            t = p.label.text()
            if t.startswith('.i'):
                ix = int(p.label.text()[2:])
                s  = sel[ix]
                l = text.textItem(str(s), anchor=4, parent=b)
                x, y = p.pos().x(), p.pos().y()
                l.setPos(x+5,y)
                l.setMutable(False)
    
    return b
    
def toMyhdlInstance(instname, connectdict, param):
    # properties end up in the connectdict
    if 'sel' in param:
        sel =  [eval(i) for i in param['sel'].split()]
    else:
        sel = [0, 1]
    inp, outp, _ = ports(param)
    s, stp = connectdict['s']
    z, ztp = connectdict['z']
    if '{' in z:
        d = dict()
        r = []
        for ix, ixy in enumerate(inp[:-1]): # skip select input (last)
            i, itp = connectdict[ixy[0]]
            if ix == len(inp)-2:
                r.append('{inp}'.format(inp=i))
            else:
                r.append('{inp} if ({s}) == {sx} else'.format(inp=i, s=s, sx=sel[ix]))
        d[z] = ' '.join(r)
        return dict(__expr__ = d)
    else:
        r =          '    @always_comb\n' 
        r +=         '    def u_{inst}():\n'.format(inst=instname)
        for ix, ixy in enumerate(inp[:-1]): # skip select input (last)
            i, itp = connectdict[ixy[0]]
#            print('Mux debug', ix, ixy, i)
            if ix == 0:
                r += '        if {s} == {sx}:\n'.format(s=s, sx=sel[ix])
            elif ix == len(inp)-2:
                r += '        else:\n'.format(s=s, ix=sel[ix])
            else:
                r += '        elif {s} == {sx}:\n'.format(s=s, sx=sel[ix])
            r += '            {z}.next = {inp}\n'.format(z=z, inp=i)
        
        return r

views = {u'icon': u'Mux.svg'}
