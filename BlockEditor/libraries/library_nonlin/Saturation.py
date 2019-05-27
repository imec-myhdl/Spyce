# cell definition
# name = 'Clip'
# libname = 'math'
tooltip = \
"""clip between min and max
optional carry:
   -1 underflow 
    0 normal
   +1 overflow"""



from  supsisim import const

inp = 1
outp = 1

parameters = dict(carry=0)
properties = dict(min='0', max='1')
#view variables:

def ports(param):
    carry = param['carry'] if 'carry' in param else 0
    w2 = 50
    inp = [('.a', -w2, 0)]

    if carry:
        outp = [('.z', w2, -const.PD), ('carry', w2, const.PD)]
    else:
        outp = [('.z', w2, 0)]

    inout = []
    return inp, outp, inout

def getSymbol(param, properties,parent=None,scene=None,):
    from  supsisim import block, text
    carry = param['carry'] if 'carry' in param else 0
    min = properties['min'] if 'min' in properties else None
    max = properties['max'] if 'max' in properties else None
    attributes = dict()
    attributes['name'] = name
    attributes['libname'] = libname
    inp, outp, _ = ports(param)
    w2 = outp[0][1]
    if carry:
        attributes['bbox']  = (-w2, -40, 2*w2, 80)
    else:
        attributes['bbox']  = (-w2, -40, 2*w2, 80)

    attributes['input'] = inp
    attributes['output'] = outp
    attributes['icon'] = views['icon']
    b = block.Block(attributes,param,properties, name, libname, parent, scene)
    # display limits
    lmin = text.textItem(str(min), anchor=7, parent=b)
    lmin.setPos(-w2+3, 20)
    lmin.setMutable(False)
    lmax = text.textItem(str(max), anchor=3, parent=b)
    lmax.setPos(w2-1, -15)
    lmax.setMutable(False)
    
    return b

    
def toMyhdlInstance(instname, connectdict, param):
    # properties end up in the connectdict
    carry = param['carry'] if 'carry' in param else 0
    min = connectdict['min'] if 'min' in connectdict else None
    max = connectdict['max'] if 'max' in connectdict else None
#    print(connectdict)
    a, atp = connectdict['.a']
    z, ztp = connectdict['.z']
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

views = {'icon':'SATUR'}
