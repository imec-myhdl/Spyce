# cell definition
# name = 'Equation'
# libname = 'math'

inp = 1
outp = 1

parameters = dict(inp = 1)
properties = dict(eq='{i0} == 0') #voor netlisten
#view variables:


def getSymbol(param, properties,parent=None,scene=None,):
    from  supsisim import const, block, text
    eq  = properties['eq'] if 'eq' in properties else '{i0} == 0'
    inp = param['inp'] if 'inp' in param else 1
    attributes = dict()
    attributes['name'] = name
    attributes['libname'] = libname

    x, y = 50, 0
    inputs = []

    for i in range(inp):
        inputs.append(('i{}'.format(i), -x, y))
        y += const.PD
                
    yy = int(y/const.PD/2)*const.PD
    outputs = [('.z', x, yy)]
    
    attributes['input'] = inputs
    attributes['output'] = outputs
    attributes['bbox'] = (-x, -const.PD, 2*x, y+2*const.PD)
    b = block.Block(attributes,param,properties, name, libname, parent, scene)
    
    # display equation
    tt = eq
    ll = text.textItem(tt, anchor=4, parent=b)
    ll.setPos(-x, y/2)
    ll.setMutable(False)
    
    return b
    
def toMyhdlInstance(instname, connectdict, param):
    # properties end up in the connectdict
    eq = connectdict['eq'] if 'eq' in connectdict else '{i0} == 0'
    inp = param['inp'] if 'inp' in param else 1
    z = connectdict['.z']
    
    inputs = dict()
    for i in range(inp):
        inputs['i{}'.format(i)] = connectdict['i{}'.format(i)]
    
    equation = eq.format(**inputs)
    

    stmt = '{}.next = {} '.format(z, equation)
    fmt = '    @always_comb\n' + \
          '    def u_{}():\n' + \
          '        {}\n'
    return fmt.format(instname, stmt)

views = {}
