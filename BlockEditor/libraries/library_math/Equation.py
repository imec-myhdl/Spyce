# cell definition
# name = 'Equation'
# libname = 'math'

from supsisim import const

inp = 1
outp = 1

parameters = dict(ninp = 1)
properties = dict(eq='{i0} == 0') #voor netlisten
#view variables:

def ports(param):
    ninp = param['ninp'] if 'ninp' in param else 1
    inp, outp, inout = [], [], []
    w2 = 50
    for ix in range(ninp):
        inp.append(('i{}'.format(ix), -w2, ix*const.PD))
    outp.append(('z', w2, (ninp//2)*const.PD))
    return inp, outp, inout
        

def getSymbol(param, properties,parent=None,scene=None,):
    from  supsisim import const, block, text
    eq  = properties['eq'] if 'eq' in properties else '{i0} == 0'
    attributes = dict()
    attributes['name'] = name
    attributes['libname'] = libname
    inp, outp, inout = ports(param)
    
    attributes['input'] = inp
    attributes['output'] = outp
    _, x0, y0 = inp[0]
    _, x1, y1 = inp[-1]
    _, x2, y2 = outp[0]
    w = x2 - x0
    h = y1 - y0
    attributes['bbox'] = [x0, y0-10, w, h + 20 + const.PD]
    b = block.Block(attributes,param,properties, name, libname, parent, scene)
    
    # display equation
    tt = eq
    ll = text.textItem(tt, anchor=5, parent=b)
    ll.setPos((x1 + x2)/2, y1 + const.PD/2 - (y0+y1)/2)
    ll.setMutable(False)
    
    return b
    
def toMyhdlInstance(instname, connectdict, param):
    # properties end up in the connectdict
    eq = connectdict['eq'] if 'eq' in connectdict else '{i0} == 0'
    ninp = param['ninp'] if 'ninp' in param else 1
    z, _ = connectdict['z']
    
    inputs = dict()
    for i in range(ninp):
        inputs['i{}'.format(i)], _ = connectdict['i{}'.format(i)]
    
    equation = eq.format(**inputs)
    

    stmt = '{}.next = {} '.format(z, equation)
    fmt = '    @always_comb\n' + \
          '    def u_{}():\n' + \
          '        {}\n'
    return fmt.format(instname, stmt)

views = {}
