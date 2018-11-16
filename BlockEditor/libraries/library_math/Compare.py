# cell definition
# name = 'Compare'
# libname = 'math'

inp = 2
outp = 1

parameters = dict(op = ('==', '< <= == >= > !='.split()))
properties = {} #voor netlisten
#view variables:


def getSymbol(param, properties,parent=None,scene=None,):
    from  supsisim import const, block, text
    operator = param['op'] if 'op' in param else '=='
    attributes = dict()
    attributes['name'] = name
    attributes['libname'] = libname
    attributes['input'] = [('a', -50, -const.PD), ('b', -50, const.PD)]
    attributes['output'] = [('.z', 50, 0)]
    b = block.Block(attributes,param,properties, name, libname, parent, scene)
    
    # create a new label in the centre
    if operator in '< <= == >= > !='.split():
        tt = operator
    else:
        tt = '=='
    ll = text.textItem('a {} b'.format(tt), anchor=5, parent=b)
    ll.setPos(10,0)
    ll.setMutable(False)
    
    return b
    
def toMyhdlInstance(instname, connectdict, param):
    # properties end up in the connectdict
    operator = param['op'] if 'op' in param else '=='
    if operator not in '< <= == >= > !='.split():
        operator = '=='
    a, b, z = connectdict['a'], connectdict['b'], connectdict['.z']


    stmt = '{}.next = {} {} {}'.format(z, a, operator, b)
    fmt = '    @always_comb\n' + \
          '    def u_{}():\n' + \
          '        {}\n'
    return fmt.format(instname, stmt)

views = {}
