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

parameters = dict(carry=0, include_max=('False', ['False', 'True']))
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
    tmin = str(properties['min']) if 'min' in properties else '0'
    tmax = str(properties['max']) if 'max' in properties else '1'
    include_max = param['include_max'][0] if 'include_max' in param else 'False'
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
    lmin = text.textItem(tmin, anchor=7, parent=b)
    lmin.setPos(-w2+3, 20)
    lmin.setMutable(False)
    if include_max == "True":
        tmax += '-1'
    lmax = text.textItem(tmax, anchor=3, parent=b)
    lmax.setPos(w2-1, -15)
    lmax.setMutable(False)
    
    return b

    
def toMyhdlInstance(instname, connectdict, param):
    # properties end up in the connectdict
    carry = param['carry'] if 'carry' in param else 0
    tmin = str(connectdict['min']) if 'min' in connectdict else '0'
    tmax = str(connectdict['max']) if 'max' in connectdict else '1'
    include_max = param['include_max'][0] if 'include_max' in param else 'False'
    if include_max == 'False':
        tmax += '-1'
#    print(connectdict)
    a, atp = connectdict['.a']
    z, ztp = connectdict['.z']
    c, ctp = connectdict['carry'] if carry else ''

    r =      '    @always_comb\n' + \
             '    def u_{inst}():\n'
    cc = carry and not '{' in c
    zz = '{' not in z
    if tmin:
        r += '        if {a} < {min}:\n'
        if zz:
            r += '            {z}.next = {min}\n'
        if cc:
            r += '            {c}.next = -1\n'

    if tmax:
        if tmin: # choose between if and elif 
            r +='        elif {a} > {max}:\n'
        else:
            r +='        if {a} > {max}:\n'
        if zz:
            r += '            {z}.next = {max}\n'
        if cc:
            r += '            {c}.next = 1\n'
    r += '        else:\n'
    r += '            {z}.next = {a}\n'
    if cc:
        r += '            {c}.next = 0\n'
    
    r = r.format(inst=instname, a=a, z=z, c=c, min=tmin, max=tmax)
    d = dict()
    tt = ''
    if '{' in z: # inline expression
        if tmin:
            tt += 'min if {a} < {min} else '
        if tmax:
            tt += '{max} if {a} > {max} else '
        tt += '{a}'
        d[z] = tt.format(a=a, z=z, c=c, min=tmin, max=tmax)
    if '{' in c:# inline expression
        if tmin:
            tt += '-1 if {a} < {min} else '
        if tmax:
            tt += '1 if {a} > {max} else '
        tt += '0'
        d[c] = tt.format(a=a, z=z, c=c, min=tmin, max=tmax)
    
    if d:
        if '.next' in r:
            return dict(__expr__ = d, __main__ = r)
        else:
            return dict(__expr__ = d)
    else:
        return r 

views = {'icon':'SATUR'}
