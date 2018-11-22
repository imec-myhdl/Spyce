# cell definition
# name = 'Mux'
# libname = 'common'

inp = 2
outp = 1

parameters = dict(channels = 2)
properties = {} #voor netlisten

from  supsisim import const

def ports(param):
    '''return inputs, outputs and inouts'''
    channels =  param['channels'] if 'channels' in param else 2
    w2, y = 50, 0
    inp = []
    for i in range(channels):
        inp.append(('i{}'.format(i), -w2, y))
        y += const.PD
            
    y += const.PD
    inp.append(('s', -w2, y))
    
    outp = [('z', w2, int(y/const.PD/2-1)*const.PD)]
    inout = []
    return inp, outp, inout

def getSymbol(param, properties, parent=None, scene=None,):
    from  supsisim import block
    attributes = dict()
    attributes['name'] = name
    attributes['libname'] = libname
    inp, outp, _ = ports(param)
    attributes['input'] = inp
    attributes['output'] = outp
    b = block.Block(attributes,param,properties, name, libname, parent, scene)
    
    
    return b
    
def toMyhdlInstance(instname, connectdict, param):
    # properties end up in the connectdict
    inp, outp, _ = ports(param)
    s, stp = connectdict['s']
    z, ztp = connectdict['z']
    r =          '    @always_comb()\n' 
    r +=         '    def u_{inst}():\n'.format(inst=instname)
    for ix, ixy in enumerate(inp[:-1]): # skip select input (last)
        i, itp = connectdict[ixy[0]]
#        print('Mux debug', ix, ixy, i)
        if ix == 0:
            r += '        if {s} == {ix}:\n'.format(s=s, ix=ix)
        elif ix == len(inp)-2:
            r += '        else:\n'.format(s=s, ix=ix)
        else:
            r += '        elif {s} == {ix}:\n'.format(s=s, ix=ix)
        r += '            {z}.next = {inp}\n'.format(z=z, inp=i)
    
    return r

views = {}
