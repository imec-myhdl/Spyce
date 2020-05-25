

from __future__ import (division, print_function, absolute_import,
                        unicode_literals)
from builtins import range
from builtins import object

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

    if not isinstance(ident, (str, str)):
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

        
class NetDescriptor(object):
    '''Decribes a net'''
    
    def __init__(self, node=None):
        self.netname     = '' # net name, or tentative name
        self.sigtype     = None # signal type
        self.driven      = False # True if driven by ipin, iopin or block output
        self.external    = False # True if connected to pin
        self.nodes       = [] # nodes on this net
        self.connections = [] # connections on this net
        self.node_coords = set() # (x,y) tuples where the net is connected (nodes)
        if node:
            self.addNode(node)
            
    def pprint(self):
        '''pretty print'''
        print('  netname           = {}'.format(self.netname))
        print('  sigtype           = {}'.format(self.sigtype))
        print('  driven            = {}'.format(self.driven ))
        print('  external          = {}'.format(self.external))
        print('  nb of nodes       = {}'.format(len(self.nodes)))
        print('  nb of connections = {}'.format(len(self.connections)))
        print('  node_coords       = {}'.format(self.node_coords))
        
    def addNode(self, node):
        '''add a node to a net and merge properties'''
        porttype = node['porttype']
        netname  = node['label']['text'].strip() if 'label' in node else ''
        sigtype  = node['signalType']['text'].strip() if 'signalType' in node else None
        xy = (node['x'], node['y'])
        
        # netname?
        if netname:
            if self.netname and netname != self.netname:
                raise Exception('name conflict on net {} while adding ()'.format(self.netname, node))
            else:
                if netname:
                    self.netname = netname
                
        # driven?
        if porttype in ['ipin', 'iopin', 'opin']:
            self.external = True
        if porttype in ['ipin', 'iopin']:
            self.driven =True
            
        # signaltype?
        if sigtype:
             if self.sigtype and sigtype != self.sigtype:
                raise Exception('type conflict on net {} while adding ()'.format(self.netname, node))
             else:
                self.sigtype = sigtype
           
        self.nodes.append(node)
        self.node_coords.add(xy)
    
    def merge(self, othernet):
        '''merge two nets'''
        if self.netname:
            if othernet.netname and self.netname != othernet.netname:
                raise Exception('Short between net {} and {}'.format(self.netname, othernet.netname))
        else:
            self.netname = othernet.netname
            
        if self.sigtype:
            if othernet.sigtype and self.sigtype != othernet.sigtype:
                raise Exception('net {} has conflicting types ({}, {})'.format(self.netname, self.sigtype, othernet.sigtype))
        else:
            self.sigtype = othernet.sigtype
        
        #merge
        self.driven |= othernet.driven
        self.nodes += othernet.nodes
        self.connections += othernet.connections
        self.node_coords |= othernet.node_coords
        return self
        

class Nets(object):
    '''holds all nets (in a diagram'''
    
    def __init__(self):
        self.named     = dict() # names must be unique, so use dict for easy lookup, elements are NetDescriptor orbjects
        self.unnamed   = [] # elements are NetDescriptor orbjects
#        self.xylookup  = dict()
        self.net_cnt   = 0 # used in anonymous nets
        self.expr_cnt  = 0 # used in anonymous inline expressions
     
    def addNode(self, node):
        rawnetname  = node['label']['text']if 'label' in node else ''
        netname = rawnetname.strip(' {}')
        if netname:
            if netname not in self.named:
                self.named[netname] = NetDescriptor(node)
            else:
                self.named[netname].addNode(node)
        else: # unnamed node
            descriptor = NetDescriptor(node)
            self.unnamed.append(descriptor)
    
    def addConnection(self, conn):
        xy0, xy1 = (conn['x0'], conn['y0']), (conn['x1'], conn['y1'])
        n0, n1 = None, None
        for nm, nt in list(self.named.items()):
            if xy0 in nt.node_coords:
                n0 = nt
                if n1:
                    break
            if xy1 in nt.node_coords:
                n1 = nt
                if n0:
                    break
                
        if n0 is None or n1 is None:
            for nt in self.unnamed:
                if xy0 in nt.node_coords:
                    n0 = nt
                    if n1:
                        break
                if xy1 in nt.node_coords:
                    n1 = nt
                    if n0:
                        break

        if n0:
            nt = n0
        elif n1:
            nt = n1
        else:
            nt = NetDescriptor()


        nt.connections.append(conn)
        # put a 'node' on the ioport locations
        nt.node_coords.add(xy0) 
        nt.node_coords.add(xy1)

        if n0 is None or n1 is None: # nothing to connect (yet)
            self.unnamed.append(nt)
            return
            
        if n0 in self.unnamed:
           self.unnamed.remove(n0)
        if n1 in self.unnamed:
           self.unnamed.remove(n1)
        
        n = n0.merge(n1)
        if not n.netname.strip(' {}'):
            self.unnamed.append(n)
            
            
    def name_all_nets(self, blocks):
        '''promote tentative names, and assign names to anonymous nets'''
        while self.unnamed:
            nn = self.unnamed.pop()
            if nn.netname == '{}': # anonymous inline expressions
                while True:
                    netname = '__anon__{}'.format(self.expr_cnt)
                    self.expr_cnt += 1
                    if netname not in self.named:
                        break
            else:
                netname = ''
                for conn in nn.connections:
                    if 'p0' in conn:
                        nn.driven = True
                        instname, portname =  conn['p0'] # name net after driving block
                        inst = blocks[instname]
                    
                        netname = 'w_{}'.format(instname.lower()) #instance_name
                        i = 0
                        while True:
                            if netname not in self.named:
                                break
                            netname = 'w_{}{}'.format(instname.lower(), i)
                            i += 1
                    if netname:
                        break
                if netname == '': # anonymous net
                    while True:
                        netname = 'w_{}'.format(self.net_cnt)
                        self.net_cnt += 1
                        if netname not in self.named:
                            break

            if '{' in nn.netname:
                netname = '{' + netname + '}'
            nn.netname = netname
            self.named[netname] = nn
         
        # connect blocks 
        for netname, nn in list(self.named.items()):
            if not nn.sigtype:
                nn.sigtype = 'bool(0)'
            for conn in nn.connections:
                for p in ['p0', 'p1']:
                    if p in conn:
                        blkname, pname = conn[p]
                        inst = blocks[blkname]
                        inst['conn'][pname] = (nn.netname, nn.sigtype)
                        
    def split_nets(self):
        '''split into internal and external nets'''
        internal_nets = dict()
        external_nets = dict()
        for netname, net in list(self.named.items()):
            if net.external:
                external_nets[netname] = net
            else:
                internal_nets[netname] = net
                
        return internal_nets, external_nets
           

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
        print ('debug netlist:' )
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
                with open(os.path.join(netlist_dir, subdir, '__init__.py'), 'w') as f:
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

        with open(filename, 'r') as fi:
            body = fi.read()
            
        txt = fillTemplate(template, blockname, body, include)
        with open(outfile, 'w') as fo:
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
            with open(outfile, 'w') as fo:
                fo.write('# diagram netlist generated from {}\n\n'.format(filename))
                fo.write(txt)
            print('diagram netlist written to', outfile)
        
        # also netlist blocks in the diagram
        for name, block in list(blocks.items()):
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
#            imp_statement = 'from {p}{l}.{b} import {b}\n'.format(p=libraries.libprefix, l=libname, b=blockname)
            imp_statement = 'from .{b} import {b}\n'.format(p=libraries.libprefix, l=libname, b=blockname)

            if os.path.isfile(modname):
                if os.path.isfile(initname):                    
                    with open(initname, 'r') as f:
                        t = f.read()
                    if not imp_statement in t:
                        t += imp_statement         
                else:
                    t = '# import blocks in name-space\n\n'
                    t += imp_statement 
                    
                with open(initname, 'w') as f:
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
        for pinname,netname in list(args.items()):
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
    hdr.append('from myhdl import Signal, concat, delay, intbv, modbv, fixbv, instances, \\')
    hdr.append('           block, always, always_seq, always_comb, instance # decorators')
    hdr.append('')


    # block definition
    bdef.append('@block\ndef {}({}):'.format(block_name, ', '.join(external_nets)))

    body.append('    # body')
    for name, inst in list(blocks.items()):
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
                for netname, expression in list(netnames.items()):
                    netname = netname.lstrip('{').rstrip('}').strip()
                    exprs[netname] = expression
            
            for path, txt in list(r.items()):
                dirname, fn = os.path.split(path)
                if not os.path.isabs(dirname):
                    dirname = os.path.join(netlist_dir, dirname)
                if dirname and not os.path.isdir(dirname):
                    os.makedirs(dirname)
                    with open(os.path.join(dirname, '__init__.py'), 'w') as f:
                        f.write('# auto generated by netlist procedure')
                fmt = const.templates['myhdl'].lstrip()
                incl = const.templates['myhdl_include']
                txt = fillTemplate(fmt, block_name, txt, incl)
                with open(os.path.join(dirname,fn), 'w') as f:
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
        if main_netlist:
            body.append(main_netlist)

    if imports:
        imp.append('# import block libraries')
        for lib in imports:
            imp.append('from . import {}'.format(lib))
        imp.append('')

    # internal_nets
    if internal_nets:
        sig.append('    # internal nets')
        for netname in sorted(internal_nets.keys()):
#            tp = internal_nets[netname]['signalType']
            tp = internal_nets[netname].sigtype
            if isidentifier(netname):
                if tp:
                    if 'Signal(' in tp:
                        sig.append('    {} = {}'.format(netname, tp))
                    else:                        
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
        for netname, expression in list(exprs.items()):
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
            for netname, expression in list(exprs.items()):
                print ('unresolved {} = {}'.format(netname, expression))
            print ('\n')
            for netname, expression in list(known_nets.items()):
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

#        inst['outp'] = set() # used to set unnamed nets that are connected to an output
        if isinstance(outp, int):
            for ix in range(outp):
                pname = '.o_{}'.format(ix)
                inst['conn'][pname] = None
#                inst['outp'].add(pname)
        else:
            for pname, px, py in outp:
                inst['conn'][pname] = None
#                inst['outp'].add(pname)

        if isinstance(inout, int):
            for ix in range(inout):
                inst['conn']['.io_{}'.format(ix)] = None
        else:
            for pname, px, py in inout:
                inst['conn'][pname] = None
        # copy keys, to signalTypes 
#        inst['signalType'].update(inst['conn'])

#==============================================================================
#   Build connectivity network
#==============================================================================
    dgm_nets = Nets() # dgm_nets hold all different nets
    for node in dgm.nodes:
        dgm_nets.addNode(node)
    for conn in dgm.connections:      
        dgm_nets.addConnection(conn)
    dgm_nets.name_all_nets(blocks)
    

#==============================================================================
# check that all block ports are connected
#==============================================================================
    for instname, inst in list(blocks.items()):
        for pin, net in list(inst['conn'].items()):
            if net is None:
                if debug:
                    print ('debug', inst['conn'])
                raise Exception('file {}: instance {}, pin {} is floating'.format(filename, instname, pin))

#==============================================================================
# spit internal and external nets
#==============================================================================
    internal_nets, external_nets = dgm_nets.split_nets()

    if debug:
         for netname, net in list(dgm_nets.named.items()):
            print('Net:', netname)
            net.pprint() 

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