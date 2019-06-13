
from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

import os, sys, string, math
import keyword
import string
from collections import OrderedDict

d = os.path.dirname(os.path.dirname(__file__))
sys.path.append(d)

#import subprocess
from   supsisim import const
from   supsisim.src_import import import_module_from_source_file
import libraries

debug=False


def isidentifier(ident):
    """Determines if string is valid Python identifier."""

    if not isinstance(ident, (str, unicode)):
        raise TypeError("expected str, but got {!r}".format(type(ident)))

    if not ident:
        return False

    if keyword.iskeyword(ident):
        return False

    first = '_' + string.lowercase + string.uppercase
    if ident[0] not in first:
        return False

    other = first + string.digits
    for ch in ident[1:]:
        if ch not in other:
            return False

    return True

filenamemyhdl_template = 'libraries.library_{}.{}'

def strip_ext(fname, ext):
    return fname[:-len(ext)] if fname.endswith(ext) else fname


def timeresolution():
    tps = 1.0/const.ticks_per_second
    si_symbols = 'yzafpnum kMGTPEZY'
    e = int(math.floor(math.log(abs(tps), 1000.0)))  # exponent
    m = tps/math.pow(1000.0, e)                      # mantissa
    if -8 <= e <= +8: # si symbol range is 1e-24 ... 1e+24
        si_symbol = si_symbols[e+8].strip()
        return '{}{}'.format(int(m+0.001), si_symbol)
 

blkModuleCache = dict()         
force_renetlist = True


def dest_newer_than_source(dest, source):
    '''return true if dest is up to date'''
    if force_renetlist:
        return False
    return os.path.isfile(dest) and (os.stat(dest).st_mtime > os.stat(source).st_mtime)

        
class NetObj(object):
    '''either connection (members are nodes/ports), or a node/port (members are connections)'''
    def __init__(self, d):
        self.netname = d['label']['text'] if 'label' in d else None
        self.type    = d['signalType']['text'] if 'signalType' in d else None
        self.members = set()
        self.d    = d
        
        
    def stamp(self, d):
        self.members.add(d)
        promotions = 0
        if d.netname and d.netname.strip('{} '):
            if self.netname and self.netname != d.netname:
                raise Exception('stamping conflict: {}, {}\non {}'.format(\
                                    self.netname, d.netname, self.d))
            elif self.netname is None:
                self.netname = d.netname
                promotions = 1
        if d.type:
            if self.type and self.type != d.type:
                raise Exception('Type conflict: {}, {}\non {}'.format(\
                                    self.type, d.type, self.d))
            elif self.type is None:
                self.type = d.type
                promotions = 1

        return promotions


           
def propagateNets(conn, connections, resolved):
    # conn is a (newly) named connection
    # connections holds UNRESOLVED nets
    # collects all connections that are tied to conn and puts them into resolved
    for node in conn.members:
        node.stamp(conn)
        resolved[conn.netname].add(conn)
        for c in node.members:
            c.stamp(node)
            if c in connections:
                connections.discard(c)
                propagateNets(c, connections, resolved)

def fillTemplate(template, blockname, body, include):
    return template.format(body   = body,
                 projectname      = const.projectname,
                 version          = const.version,
                 copyrightText    = const.copyrightText,
                 copyrightPolicy  = const.copyrightPolicy,
                 ticks_per_second = const.ticks_per_second,
                 t_stop           = const.t_stop,
                 blockname        = blockname,
                 user             = os.getlogin(),
                 t_resolution     = timeresolution(),
                 include          = include)
    

#==============================================================================
# main netlist routine
#==============================================================================
def netlist(filename, properties=dict(), lang='myhdl', netlist_dir=const.netlist_dir, netlists = None):
    '''netlist a file in netlist_dir
    netlists contains a set of already netlisted blocks'''
    if debug:
        print ('debug netlist' )
        print ('      filename   ', filename)
        print ('      properties ', properties)
        print ('      lang       ', lang)
#    print ('      netlist_dir', netlist_dir)
#    print ('      netlists   ', netlists)
    if netlists is None:
        netlists = set()
    # check if already netlisted
    if filename in netlists:
#        print('skip')
        return
        
    toplevel = len(netlists) == 0
    netlists.add(filename)
    
    ed, ext_diagram = const.viewTypes['diagram']
    ed, ext_lang    = const.viewTypes[lang]

#    d, module_name  = os.path.split(filename)
    
    libname, blockname = libraries.pathToLibnameBlockname(filename) # removes extension
    ext = '.py' if lang == 'myhdl' else ext_lang # .mhdl.py -> .py etc.
    
    # note: libdir is empty when outside library i.e. toplevel
    if toplevel:
        subdir = ''
    else:
        subdir = libraries.libprefix + libname  if libname else libname 
        if not os.path.isdir(os.path.join(netlist_dir, subdir)):
            os.makedirs(os.path.join(netlist_dir, subdir))
            if lang == 'myhdl':
                with open(os.path.join(netlist_dir, subdir, '__init__.py'), 'wb') as f:
                    f.write('# import blocks in name-space\n\n')
        
    outfile = os.path.join(netlist_dir, subdir, blockname + ext)


    if lang == 'myhdl':
        template     = const.templates['myhdl'].lstrip()
        tbfooter     = const.templates['myhdl_tbfooter']
        convert      = toMyhdl
        codegen_stmt = 'toMyhdlInstance'
        if toplevel:
            include = const.templates['myhdl_toplevel_include'] 
        else: 
            include = const.templates['myhdl_include']
    elif lang == 'systemverilog':
        template     = const.templates['systemverilog'].lstrip()
        tbfooter     = const.templates['systemverilog_tbfooter']
        convert      = toSystemverilog
        codegen_stmt = 'toSytemverilogInstance'
        if toplevel:
            include = const.templates['systemverilog_toplevel_include'] 
        else: 
            include = const.templates['systemverilog_include']
    else:
        raise Exception('todo: language support for '+lang)           


    if filename.endswith(ext_lang): # other view (myhdl verilog etc.)
        # copy file to netlist location (if newer than existing netlist)
        if outfile in netlists or dest_newer_than_source(dest=outfile, source=filename):
            # print('{} module already present in {}'.format(lang, outfile))
            return # do nothing if outfile newer than infile

        with open(filename, 'rb') as fi:
            body = fi.read()
            
        txt = fillTemplate(template, blockname, body, include)
        with open(outfile, 'wb') as fo:
            fo.write(txt)
        print('{} module written to {}'.format(lang, outfile))

        
    else: # diagram

        # resolve connections
        blocks, internal_nets, external_nets = resolve_dgm_connectivity(filename, properties=dict())
        body = convert(blockname, blocks, internal_nets, external_nets, netlist_dir)
            
        txt = fillTemplate(template+tbfooter, blockname, body, include)

        if not os.path.isdir(netlist_dir):
            os.makedirs(netlist_dir)

        if not dest_newer_than_source(dest=outfile, source=filename):
            with open(outfile, 'wb') as fo:
                fo.write('# diagram netlist generated from {}\n\n'.format(filename))
                fo.write(txt)
            print('diagram netlist written to', outfile)
        
        # also netlist blocks in the diagram
        for name, block in blocks.items():
            libname, blockname = block['libname'], block['blockname']
#            print ('subblock', libname, blockname)
            k = libname + '/' + blockname
            libpath = libraries.libpath(libname)
            fname = os.path.join(libpath, blockname)
#                netlist_subdir = os.path.join(netlist_dir, libraries.libprefix+libname)
            
            # block module contains code genration (no need to netlist)
            if k in blkModuleCache and hasattr(blkModuleCache[k], codegen_stmt):
                continue

            # inst has a netlist view
            elif os.path.exists(fname + ext_lang):
                netlist(fname + ext_lang, properties, lang, netlist_dir, netlists)

            # inst has diagram (that can be netlisted)
            elif os.path.exists(fname + ext_diagram):
                netlist(fname + ext_diagram, properties, lang, netlist_dir, netlists)

            else:
                print('Warning: {}.{} is missing a {} view or diagram'.format(libname, blockname, lang))

            if lang != 'myhdl':
                continue
            
            # add __init__ files as needed
            # and add 'from library import block'
            # this allows the instantiation to look like:
            #     library.block(pin1=net1, pin2=net2)
            # otherwise instantiation would look like: 
            #     library.block.block(pin1=net1, pin2=net2)
            libdir = libraries.libprefix + libname if libname else libname
            initname = os.path.join(netlist_dir, libdir, '__init__.py')
            modname = os.path.join(netlist_dir, libdir, blockname+'.py')
            imp_statement = 'from {p}{l}.{b} import {b}\n'.format(p=libraries.libprefix, l=libname, b=blockname)

            if os.path.isfile(modname):
                if os.path.isfile(initname):                    
                    with open(initname, 'rb') as f:
                        t = f.read()
                    if not imp_statement in t:
                        t += imp_statement         
                else:
                    t = '# import blocks in name-space\n\n'
                    t += imp_statement 
                    
                with open(initname, 'wb') as f:
                   f.write(t)


           

    

def instToMyhdl(inst):
    '''returns tuple (text, isimport'''
    libname, blkname = inst['libname'], inst['blockname']
    name = inst['label']['text'] # instance name in diagram

    args = inst['conn']
    # store properties
    if 'properties' in inst:
        args.update(inst['properties'])

    
    parameters = inst['parameters'] if 'parameters' in inst else dict() # pcell
        
    
    instance_netlist = ''

    # find inst module
    k = libname+'/'+blkname
    try: 
        blkMod = blkModuleCache[k]
    except KeyError:
        fname = libraries.blockpath(libname, blkname)
        blkMod = import_module_from_source_file(fname)
        blkModuleCache[k] = blkMod
    
    # try module.toMyhdlInstance()
    try:
        instance_netlist = blkMod.toMyhdlInstance(name, args, parameters)
        return instance_netlist, False

    except AttributeError:
        if parameters: # parametrized cell should have netlist function
            message = 'error while netlisting parametrized block {}.{}\n'.format(libname, blkname) + \
                      'function toMyhdlInstance is not present.'
            raise Exception(message)

    if not instance_netlist: # normal cell netlist
        #instance_netlist = defaultMyHdlInstance(name, libname, blkname, args)
        conns = []
        for pinname,netname in args.items():
            if isinstance(netname, (list, tuple)):
                netname = netname[0]
            conns.append('{} = {}'.format(pinname, netname))
        jj = ',\n' + ' ' * 12
        c = jj.join(conns)
        return '    u_{} = {}{}.{}({})\n'.format(name, libraries.libprefix, libname, blkname, c), True




def toMyhdl(block_name, blocks, internal_nets, external_nets, netlist_dir):
    '''block_name        string with the name of the block
       blocks            dict {inst_name:block definitions (from diagram) + resolved connectivity}
       external_nets     dict external_nets[netname] = signalType containing all portnames 
       internal_nets     dict internal_nets[netname] = signalType containing all internal netnames 
    '''
    hdr  = [] # header
    imp  = [] # import defs
    sig  = [] # signal defs
    bdef, body = [], [] # block def, block body
    exprs = dict() # of expressions (to be resolved)

    # set of library imports
    imports = set()

#    hdr.append('TIME_UNIT = {}'.format(const.ticks_per_second))
    hdr.append('')
    hdr.append('from myhdl import Signal, concat, delay, intbv, fixbv, instances, \\')
    hdr.append('           block, always, always_seq, always_comb, instance # decorators')
    hdr.append('')


    # block definition
    bdef.append('@block\ndef {}({}):'.format(block_name, ', '.join(external_nets)))

    body.append('    # body')
    for name, inst in blocks.items():
        r, isimport = instToMyhdl(inst)
        if isimport:
            imports.add(libraries.libprefix + inst['libname'])
        if isinstance(r, dict):
            # additional files keys=filename ( __main__ for main file),  values=text,
            main_netlist = r.pop('__main__') if '__main__' in r else ''
            signals_netlist = r.pop('__signals__') if '__signals__' in r else ''

            if '__defs__' in r:
                defs_netlist = r.pop('__defs__')
                bdef.append(defs_netlist)

            if '__expr__' in r:
                netnames = r.pop('__expr__')
                for netname, expression in netnames.items():
                    netname = netname.lstrip('{').rstrip('}').strip()
                    exprs[netname] = expression
            
            for path, txt in r.items():
                dirname, fn = os.path.split(path)
                if not os.path.isabs(dirname):
                    dirname = os.path.join(netlist_dir, dirname)
                if dirname and not os.path.isdir(dirname):
                    os.makedirs(dirname)
                    with open(os.path.join(dirname, '__init__.py'), 'wb') as f:
                        f.write('# auto generated by netlist procedure')
                fmt = const.templates['myhdl'].lstrip()
                incl = const.templates['myhdl_include']
                txt = fillTemplate(fmt, block_name, txt, incl)
                with open(os.path.join(dirname,fn), 'wb') as f:
                    f.write(txt)
                if signals_netlist:
                    for line in signals_netlist.splitlines():
                        if '=' in line:
                            a, _, _ = line.partition('=')
                            a = a.strip()
                            if a and a in internal_nets:
                                internal_nets.pop(a)
                    sig.append(signals_netlist)
        else:            
            main_netlist = r
        
        body.append(main_netlist)

    if imports:
        imp.append('# import block libraries')
        for lib in imports:
            imp.append('import {}'.format(lib))
        imp.append('')

    # internal_nets
    if internal_nets:
        sig.append('    # internal nets')
        for netname in sorted(internal_nets.keys()):
            tp = internal_nets[netname]['signalType']
            if isidentifier(netname):
                if tp:
                    sig.append('    {} = Signal({})'.format(netname, tp))
                else:
                    sig.append('    {} = Signal(bool(0))'.format(netname))
        sig.append('')

    body.append('    return instances()')
    bdef.append('')
    
    known_nets = dict()
    for k in internal_nets:
        if not '{' in k:
            known_nets[k] = k
    for k in external_nets:
        known_nets[k] = k
           
    
    while exprs:
        found = None
        for netname, expression in exprs.items():
            try:
                s = expression.format(**known_nets)
                known_nets[netname] = s
                found = netname
                break
            except KeyError:
                continue

        if found:
            exprs.pop(found)
        else:
            for netname, expression in exprs.items():
                print ('unresolved {} = {}'.format(netname, expression))
            print ('\n')
            for netname, expression in known_nets.items():
                print ('  resolved {} = {}'.format(netname, expression))
                
            raise Exception('Not able to resolve expressions')
        
                
            
            
    r =  '\n'.join(hdr+imp+bdef+sig+body)
    if debug:
        print (r)
    return r.format(**known_nets)


def resolve_dgm_connectivity(filename, properties=dict()):
    '''work out the connections in a diagram'''
    #import file
    dgm = import_module_from_source_file(filename)
    
#==============================================================================
#   read blocks
#==============================================================================
    blocks = dict()
    for inst in dgm.blocks:
        inst_name = inst['label']['text']
        blocks[inst_name] = inst

        blockname, libname = inst['blockname'],  inst['libname']
        fname = libraries.blockpath(libname, blockname)
        k = blockname+'/'+libname
        if not k in blkModuleCache:
            blkModuleCache[k] = import_module_from_source_file(fname)
        blkMod = blkModuleCache[k]

        if 'parameters' in inst:
            param = inst['parameters']
            if hasattr(blkMod, 'ports'):
                inp, outp, inout = blkMod.ports(param)
            else:
                inp = param['inp'] if 'inp' in param else []
                outp = param['outp'] if 'outp' in param else []
                inout = param['inout'] if 'inout' in param else []
        else:
            inp, outp, inout = blkMod.inp, blkMod.outp, []

        # first initialize the connection to each pin to None
        inst['conn'] = OrderedDict()
#        inst['signalType'] = OrderedDict()
        if isinstance(inp, int):
            for ix in range(inp):
                inst['conn']['.i_{}'.format(ix)] = None
        else:
            for pname, px, py in inp:
                inst['conn'][pname] = None

        inst['outp'] = set() # used to set unnamed nets that are connected to an output
        if isinstance(outp, int):
            for ix in range(outp):
                pname = '.o_{}'.format(ix)
                inst['conn'][pname] = None
                inst['outp'].add(pname)
        else:
            for pname, px, py in outp:
                inst['conn'][pname] = None
                inst['outp'].add(pname)

        if isinstance(inout, int):
            for ix in range(inout):
                inst['conn']['.io_{}'.format(ix)] = None
        else:
            for pname, px, py in inout:
                inst['conn'][pname] = None
        # copy keys, to signalTypes 
#        inst['signalType'].update(inst['conn'])



    resolved   = dict()# resolved connections resolved[netname] == set(connections and nodes)
    unresolved = set() # unresolved connections

            
    # create names for {} (anonymous inline expressions)
    anon_exprs  = 0
    for n in dgm.nodes:
        if 'label' in n and n['porttype'] == 'node':
            if n['label']['text'].strip(' {}') == '': # auto_name {} inline-expressions
                n['label']['text'] = '{{__anon__{}}}'.format(anon_exprs)
                anon_exprs += 1

    # find pins because they are external nets
    pinnames = set()            
    nodes = dict()
    for n in dgm.nodes:
        xy  = n['x'], n['y']
        nodes[xy] = NetObj(n)
        if 'label' in n and n['porttype'] != 'node':
            pinnames.add(n['label']['text'])

    # create dummy connection for named nodes
    for n in dgm.nodes:
        if 'label' in n: 
            x, y = n['x'], n['y']
            dgm.connections.append(dict(x0=x, y0=y, x1=x, y1=y))

    for c in dgm.connections:
        conn = NetObj(c)
        if debug:
            print('connection', c)
        for xy in [(c['x0'], c['y0']), (c['x1'], c['y1'])]:
            if xy in nodes:
                conn.stamp(nodes[xy])
                nodes[xy].stamp(conn)
        if conn.netname:
            if conn.netname not in resolved:
                resolved[conn.netname] = set()
            resolved[conn.netname].add(conn)
        else:
            unresolved.add(conn)
            
#==============================================================================
# propagate named nets
#==============================================================================
    for netname in resolved.keys():
        for conn in set(resolved[netname]):
            propagateNets(conn, unresolved, resolved)
 
#==============================================================================
#  propagate anonymous nets
#==============================================================================
    # build a set of driven nets    
    driven_connections = set()
    for conn in unresolved:
        if 'p0' in conn.d:
            driven_connections.add(conn)

    n_nets = 0 # used to number anonymous nets
    while unresolved:
        
        # check if there are driven conncetions
        if driven_connections: # name after driving instance
            conn = driven_connections.pop()
            unresolved.discard(conn)                   
            instname, portname =  conn.d['p0']
            inst = blocks[instname]
            
            netname = 'w_{}'.format(instname.lower()) #instance_name
            i = ''
            # make sure it does not yet exists
            while True:
                n = '{}{}'.format(netname, i)
                if n not in resolved:
                    break
                i = i+1 if i else 1
                if i == 100:
                    raise Exception('cannot generate unique name: '+netname)

            netname = n
            if portname in inst['outp']:
               netname = 'w_{}'.format(instname.lower()) #instance_name
               if len(inst['outp']) > 1: # not the only output
                   netname += '_{}'.format(portname.lstrip('.').lower()) # + port_name
            else:
                if debug:
                    print(inst)
                    print('resolved')
                    for c in resolved:
                        print(c.netname)
                raise Exception('{}: connection to {} pin {} is not an output of {}.{}'.format(filename, instname, portname, inst['libname'], inst['blockname']))
                        
        else: # choose arbitrary name
            conn = unresolved.pop()
            if debug:
                print ('anonymous net in ', filename)
                print ('   p0 = {}, {}'.format(conn.d['x0'],conn.d['y0']))
                print ('   p1 = {}, {}'.format(conn.d['x1'],conn.d['y1']))
            n_nets += 1
            netname = 'net{}'.format(n_nets)
            
        conn.netname = netname
        if conn.netname not in resolved:
            resolved[conn.netname] = set()
        resolved[conn.netname].add(conn)
        propagateNets(conn, unresolved, resolved)

   
#==============================================================================
# resolve connection to blocks
#==============================================================================
        
    for netname, conns in resolved.items():
        for conn in conns:
            for p in ['p0', 'p1']:
                if p in conn.d:
                    blkname, pname = conn.d[p]
                    inst = blocks[blkname]
                    inst['conn'][pname] = (conn.netname, conn.type)
       
    # check that all block ports are connected
    for instname, inst in blocks.items():
        for pin, net in inst['conn'].items():
            if net is None:
                if debug:
                    print ('debug', inst['conn'])
                raise Exception('file {}: instance {}, pin {} is floating'.format(filename, instname, pin))
#                print('file {}: instance {}, pin {} is not Connected'.format(filename, instname, pin))

    internal_nets = dict()
    external_nets = dict()
    for netname in resolved:
        # signal_type
        st = None
        for item in resolved[netname]:
            if item.type:
                if st is None:
                    st = item.type
                elif st != item.type:
                    raise Exception('Type conflict: {}, {}\non {}'.format(\
                                    st, item.type, item))
        prop = dict(signalType = st)
        for c in resolved[netname]:
            if 'properties' in c.d:
                prop.update(c.d['properties'])

        if netname in pinnames:
            external_nets[netname] = prop
        else:
            internal_nets[netname] = prop
    
    return blocks, internal_nets, external_nets
  
        
    
if __name__ == "__main__":
    lang = 'myhdl'
#    fname = os.path.join(d, 'saves', 'untitled.py')
#    fname = os.path.join(d, 'saves', 'test.py')
    fname = sys.argv[1]
    nldir = os.path.join(const.netlist_dir + '_' + lang, strip_ext(os.path.basename(fname), '.py'))
    debug=True
    netlist(fname, netlist_dir=nldir)
    print('done')