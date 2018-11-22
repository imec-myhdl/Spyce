
from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

import os, sys, string
from collections import OrderedDict

d = os.path.dirname(os.path.dirname(__file__))
sys.path.append(d)

import subprocess
from   supsisim import const 
from   supsisim.src_import import import_module_from_source_file
import libraries

filenameTemplate = 'libraries.library_{}.{}'

def strip_ext(fname, ext):
    return fname[:-len(ext)] if fname.endswith(ext) else fname


template = """
#---------------------------------------------------------------------------------------------------
# Project   : {projectname}
# Filename  : {blockname}_myhdl.py
# Version   : 1.0
# Author    : {user}
# Contents  : Python {blockname} model 
# Copyright : {copyrightText}
#             *** {copyrightPolicy} ***
#---------------------------------------------------------------------------------------------------


#-- import -----------------------------------------------------------------------------------------

{imp}

from myhdl import Signal, instance, instances, block

#-- code ---------------------------------------------------------------------------------

@block
def {blockname}({params}):

    {signals}
    
    
    
    {instances}
    
    
    
    return instances()    
    
if __name__ == "__main__":
# =============================================================================
#     setup and run testbench
# =============================================================================

    from myhdl import traceSignals    
    
    @block
    def {blockname}_tb():
        {tbText}
        
    tb = {blockname}_tb()
    traceSignals.timescale = '1fs'    
    tb.config_sim(trace=True)
    tb.run_sim()
"""

blkModuleCache = dict()         
force_renetlist = True
netlists = set()

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
        if d.netname:
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

#==============================================================================
# main netlist routine
#==============================================================================
def netlist(filename, properties=dict(), lang='myhdl', netlist_dir=const.netlist_dir):
    if filename in netlists:
        return
    netlists.add(filename)
    d, module_name  = os.path.split(filename)
    ed, ext_diagram = const.viewTypes['diagram']
    ed, ext_lang    = const.viewTypes[lang]
    
    if filename.endswith(ext_lang): # other view (myhdl verilog etc.)
        # copy file to netlist location (if newer than existing netlist)
    
        libname, blockname = libraries.pathToLibnameBlockname(strip_ext(filename, ext_lang))
        ext = '.py' # .mhdl.py -> .py etc.
        
        libdir = libraries.libprefix + libname  if libname else libname
            
        outfile = os.path.join(netlist_dir, libdir, blockname + ext)
        if outfile in netlists or dest_newer_than_source(dest=outfile, source=filename):
            # print('{} module already present in {}'.format(lang, outfile))
            return # do nothing if outfile newer than infile

        if not os.path.isdir(os.path.join(netlist_dir, libdir)):
            os.makedirs(os.path.join(netlist_dir, libdir))
        with open(filename, 'rb') as fi:
            t = fi.read()
            
        with open(outfile, 'wb') as fo:
            fo.write(t)
        print('{} module written to {}'.format(lang, outfile))

        
    else: # diagram
        if filename.endswith(ext_diagram):
            module_name = strip_ext(os.path.basename(filename), ext_diagram)
        else:
            module_name = strip_ext(module_name, '.py') # toplevel can have arbitrary_name.py

        libname, _ = libraries.pathToLibnameBlockname(strip_ext(filename, ext_lang))
        libdir = libraries.libprefix + libname  if libname else libname

        # resolve connections
        blocks, internal_nets, external_nets = resolve_connectivity(filename, properties=dict())

        if lang == 'myhdl':
            txt = toMyhdl(module_name, blocks, internal_nets, external_nets)

            if not os.path.isdir(netlist_dir):
                os.makedirs(netlist_dir)

            fname = os.path.join(netlist_dir, libdir, module_name + '.py')
            if not dest_newer_than_source(dest=fname, source=filename):
                with open(fname, 'wb') as fo:
                    fo.write('# myhdl netlist generated from {}\n\n'.format(filename))
                    fo.write(txt)
                print('diagram netlist written to', fname)
            
            for name, block in blocks.items():
                libname, blockname = block['libname'], block['blockname']
                k = libname + '/' + blockname
                libpath = libraries.libpath(libname)
                fname = os.path.join(libpath, blockname)
                netlist_subdir = os.path.join(netlist_dir, libraries.libprefix+libname)
                
                # inst contains toMyhdlInstance code 
                if k in blkModuleCache and hasattr(blkModuleCache[k], 'toMyhdlInstance'):
                    pass

                # inst has a netlist view
                elif os.path.exists(fname + ext_lang):
                    netlist(fname + ext_lang, properties, lang, netlist_dir)

                # inst has diagram (that can be netlisted)
                elif os.path.exists(fname + ext_diagram):
                    netlist(fname + ext_diagram, properties, lang, netlist_dir)

                else:
                    print('Warning: {}.{} is missing a {} view'.format(libname, blockname, lang))
    

        else:
            raise Exception('todo: language support for '+lang)

    

def instToMyhdl(inst):
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
        return instance_netlist

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
        return '    u_{} = {}{}.{}({})\n'.format(name, libraries.libprefix, libname, blkname, c)




def toMyhdl(module_name, blocks, internal_nets, external_nets):
    '''module_name       string with the name of the module
       blocks            dict {inst_name:block definitions (from diagram) + resolved connectivity}
       external_nets     dict external_nets[netname] = signalType containing all portnames 
       internal_nets     dict internal_nets[netname] = signalType containing all internal netnames 
    '''

    ret = ['from myhdl import block, Signal, intbv, fixbv, instances\n']

    # imports
    imports = set()
    for name, inst in blocks.items():
        imports.add(libraries.libprefix + inst['libname'])
    
    ret.append('# import block libraries')
    for lib in imports:
        ret.append('import {}'.format(lib))
    ret.append('')
    
    # block definition
    ret.append('@block\ndef {}({}):'.format(module_name, ', '.join(external_nets)))
    ret.append('')

    # internal_nets
    if internal_nets:
        ret.append('    # internal nets')
        for netname in internal_nets:
            tp = internal_nets[netname]['signalType']
            if netname[0] in '_' + string.lowercase + string.uppercase:
                if tp:
                    ret.append('    {} = Signal({})'.format(netname, tp))
                else:
                    ret.append('    {} = Signal(0)'.format(netname))
        ret.append('')


    # blocks
    ret.append('    # body')
    for name, inst in blocks.items():
        ret.append(instToMyhdl(inst))

    ret.append('    return instances()')
            
    return  '\n'.join(ret)


def resolve_connectivity(filename, properties=dict()):
    
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

    # find pins because they are external nets
    pinnames = set()            
    nodes = dict()
    for n in dgm.nodes:
        xy  = n['x'], n['y']
        nodes[xy] = NetObj(n)
        if 'label' in n and n['porttype'] != 'node':
            pinnames.add(n['label']['text'])


    resolved   = dict()# resolved connections resolved[netname] == set(connections and nodes)
    unresolved = set() # unresolved connections

    for c in dgm.connections:
        conn = NetObj(c)
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
# propagate names nets
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
            if portname in inst['outp']:
               netname = 'w_{}'.format(instname.lower()) #instance_name
               if len(inst['outp']) > 1: # not the only output
                   netname += '_{}'.format(portname.lstrip('.').lower()) # + port_name
            else:
                raise Exception('{}: connection to {} pin {} is not an output of {}.{}'.format(filename, instname, portname, inst['libname'], inst['blockname']))
                        
        else: # choose arbitrary name
            conn = unresolved.pop()
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
                raise Exception('file {}: instance {}, pin {} is not Connected'.format(filename, instname, pin))

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
    fname = os.path.join(d, 'saves', 'test.py')
    nldir = os.path.join(const.netlist_dir + '_' + lang, strip_ext(os.path.basename(fname), '.py'))
    netlist(fname, netlist_dir=nldir)
    print('done')