# -*- coding: utf-8 -*-

tooltip = \
"""Interface like funtionality: like in SystemVerilog. 
Suited for central registers etc.

reg_names specifies which names should be extracted"""

# cell definition
# name = 'Interface'
# libname = 'common'
from  spycelib import const

inp = []
outp = []

parameters = dict(reg_names = 'reg1')
properties = {} # for netlisting
#view variables:

def ports(param):
    reg_names = param['reg_names'] if 'reg_names' in param else 'reg1'
    reg_names = reg_names.replace(', ', ' ').split()
    w2 = 100
    inp, outp, inout = [], [], []

    # inp
    inp.append(('reg', -w2, -const.PD))    

    # outp
    for ix, pname in enumerate(reg_names):
        outp.append((pname, w2, ix * const.PD))
    return inp, outp, inout
    

def getSymbol(param, properties,parent=None,scene=None,):
    import spycelib.block
    attributes = dict()
    attributes['name'] = name
    attributes['libname'] = libname
    inp, outp, _ = ports(param)
    attributes['input'] = inp
    attributes['output'] = outp
    b = spycelib.block.Block(attributes,param,properties, name, libname, parent, scene)
                 
    return b
    
def toMyhdlInstance(instname, connectdict, param):
    # properties end up in the connectdict
    inp, outp, _ = ports(param)
    
    r  = []
    reg, tp = connectdict[inp[0][0]]
    for pname, x, y in outp:
        netname, tp = connectdict[pname]
        r.append('{nn}.next = {r}.{pn}'.format(nn = netname, pn = pname, r = reg))
        
    assigns = '\n        '.join(r)
    fmt = '    # instance {i}\n' + \
          '    @always_comb\n' + \
          '    def u_{i}():\n' + \
          '        {a}\n'
    return fmt.format(i=instname, a=assigns)

views = {}
