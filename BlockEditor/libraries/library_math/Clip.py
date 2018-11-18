# cell definition
# name = 'Clip'
# libname = 'math'
from  supsisim import const

inp = 1
outp = 1

parameters = dict(carry=0)
properties = dict(min='0', max='1') #voor netlisten
#view variables:

def ports(param):
    carry = param['carry'] if 'carry' in param else 0
    w2 = 50
    inp, outp = [('.a', -w2, 0)], [('.z', w2, -const.PD)]

    if carry:
        outp.append(('carry', w2, const.PD))

    inout = []
    return inp, outp, inout

def getSymbol(param, properties,parent=None,scene=None,):
    from  supsisim import block, text
    carry = param['carry'] if 'carry' in param else 0
    min = eval(properties['min']) if 'min' in properties else None
    max = eval(properties['max']) if 'max' in properties else None
    attributes = dict()
    attributes['name'] = name
    attributes['libname'] = libname
    inp, outp, _ = ports(param)
    w2 = outp[0][1]
    if carry:
        attributes['bbox']  = (-w2, -1.5*const.PD, 2*w2, 3*const.PD)
    else:
        attributes['bbox']  = (-w2, -const.PD, 2*w2, 2*const.PD)

    attributes['input'] = inp
    attributes['output'] = outp
    b = block.Block(attributes,param,properties, name, libname, parent, scene)
    # display equation
    tt = '[{}, {}]'.format(min, max)
    ll = text.textItem(tt, anchor=5, parent=b)
#    ll.setPos(-x, y/2)
    ll.setMutable(False)
    
    return b

    
def toMyhdlInstance(instname, connectdict, param):
    # properties end up in the connectdict
    carry = param['carry'] if 'carry' in param else 0
    min = eval(connectdict['min']) if 'min' in connectdict else None
    max = eval(connectdict['max']) if 'max' in connectdict else None
#    print(connectdict)
    a, z = connectdict['.a'], connectdict['.z']
    c = connectdict['carry'] if carry else None

    r =      '    @always_comb\n' + \
             '    def u_{inst}():\n'

    if not min is None:
        r += '        if {a} < {min}:\n'
        r += '            {z}.next = {min}\n'
        if carry:
            r += '            {c}.next = -1\n'

    if not max is None:
        if min is None: # choose between if and elif 
            r +='        if {a} > {max}:\n'
        else:
            r +='        elif {a} > {max}:\n'
        r += '            {z}.next = {max}\n'
        if carry:
            r += '            {c}.next = 1\n'
    r += '        else:\n'
    r += '            {z}.next = {a}\n'
    if carry:
        r += '            {c}.next = 0\n'
        
    return r.format(inst=instname, a=a, z=z, c=c, min=min, max=max)

views = {}
