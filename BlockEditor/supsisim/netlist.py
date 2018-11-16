
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

def dest_newer_than_source(dest, source):
    if force_renetlist:
        return False
    return os.path.isfile(dest) and (os.stat(dest).st_mtime > os.stat(source).st_mtime)

        
class NetObj(object):
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


def netlist(filename, properties=dict(), lang='myhdl', netlist_dir=const.netlist_dir):
    d, module_name  = os.path.split(filename)
    ed, ext_diagram = const.viewTypes['diagram']
    ed, ext_lang    = const.viewTypes[lang]
    
    if filename.endswith(ext_lang): # other view (myhdl verilog etc.)
        # copy file to netlist location (if newer than existing netlist)
    
        libname, blockname = libraries.pathToLibnameBlockname(strip_ext(filename, ext_lang))
        ext = '.py' # .mhdl.py -> .py etc.
        
        libdir = libraries.libprefix + libname  if libname else libname
            
        outfile = os.path.join(netlist_dir, libdir, blockname + ext)
        if dest_newer_than_source(dest=outfile, source=filename):
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
                
                # blk contains toMyhdlInstance code 
                if k in blkModuleCache and hasattr(blkModuleCache[k], 'toMyhdlInstance'):
                    pass

                # blk has a netlist view
                elif os.path.exists(fname + ext_lang):
                    netlist(fname + ext_lang, properties, lang, netlist_dir)

                # blk has diagram (that can be netlisted)
                elif os.path.exists(fname + ext_diagram):
                    netlist(fname + ext_diagram, properties, lang, netlist_dir)

                else:
                    print('Warning: {}.{} is missing a {} view'.format(libname, blockname, lang))
    

        else:
            raise Exception('todo: language support for '+lang)

    

def defaultMyHdlInstance(name, libname, blockname, connectDict):
    conns = []
    for pinname,netname in connectDict.items():
        conns.append('{} = {}'.format(pinname, netname))
    jj = ',\n' + ' ' * 12
    c = jj.join(conns)
    return '    u_{} = {}{}.{}({})\n'.format(name, libraries.libprefix, libname, blockname, c)

def blkToMyhdlInstance(blk):
    
    libname, blkname = blk['libname'], blk['blockname']
    name = blk['label']['text'] # instance name in diagram

    args = blk['conn']
    # store properties
    if 'properties' in blk:
        args.update(blk['properties'])

    
    parameters = blk['parameters'] if 'parameters' in blk else dict() # pcell
        
    
    instance_netlist = ''

    # find blk module
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
                      'function toMyhdlInstance is not present. \n' +\
                      'When the parameters do not change ports, you can return None to indicate normal netlist'
            raise Exception(message)

    if not instance_netlist: # normal cell netlist
        instance_netlist = defaultMyHdlInstance(name, libname, blkname, args)

    return instance_netlist


def toMyhdl(module_name, blocks, internal_nets, external_nets):
    '''module_name       string with the name of the module
       blocks            dict {inst_name:block definitions (from diagram) + resolved connectivity}
       external_nets     dict {netname:signalType} containing all portnames 
       internal_nets     dict {netname:signalType} containing all internal netnames 
    '''

    ret = ['from myhdl import block, Signal, intbv, fixbv, instances\n']
    
    # imports
    imports = set()
    for name, blk in blocks.items():
        imports.add(libraries.libprefix + blk['libname'])
    
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
    for name, blk in blocks.items():
        ret.append(blkToMyhdlInstance(blk))

    ret.append('    return instances()')
            
    return  '\n'.join(ret)


def resolve_connectivity(filename, properties=dict()):
    
    #import file
    dgm = import_module_from_source_file(filename)
    
#==============================================================================
#   read blocks
#==============================================================================
    blocks = dict()
    for blk in dgm.blocks:
        inst_name = blk['label']['text']
        blocks[inst_name] = blk

        blockname, libname = blk['blockname'],  blk['libname']
        fname = libraries.blockpath(libname, blockname)
        k = blockname+'/'+libname
        if not k in blkModuleCache:
            blkModuleCache[k] = import_module_from_source_file(fname)

    portnames = set()            
    nodes = dict()
    for n in dgm.nodes:
        xy  = n['x'], n['y']
        nodes[xy] = NetObj(n)
        if 'label' in n and n['porttype'] != 'node':
            portnames.add(n['label']['text'])


    resolved   = dict()# resolved connections netname:[list of connections and nodes]
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
            
            # check how many outputs in block
            blk = blocks[instname]
            libname   = blk['libname']
            blockname = blk['blockname']
            k = blockname+'/'+libname
            
            print ('debug', libname, blockname, instname, portname)
            blkMod = blkModuleCache[k]
            if hasattr(blkMod, 'ports'):
                param = blk['parameters'] if 'parameters' in blk else None
                _, outp, _ = blkMod.ports(param)
                noutp = len(outp)
            else:
                if isinstance(blkMod.outp, int):
                    noutp = blkMod.outp
                else:
                    noutp = len(blkMod.outp)
            netname = 'w_{}'.format(instname.lower()) #instance_name
            if noutp > 1: # when more than 1 output
                netname += '_{}'.format(portname.lstrip('.').lower()) # + port_name
            
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
    for blkname, blk in blocks.items():
        blockname, libname = blk['blockname'],  blk['libname']
        k = blockname+'/'+libname
        blkMod = blkModuleCache[k]
        
        inp, outp = blkMod.inp, blkMod.outp
        blk['conn'] = OrderedDict()
        if isinstance(inp, int):
            for ix in range(inp):
                blk['conn']['.i_{}'.format(ix)] = None
        else:
            for pname, px, py in inp:
                blk['conn'][pname] = None
        if isinstance(outp, int):
            for ix in range(outp):
                blk['conn']['.o_{}'.format(ix)] = None
        else:
            for pname, px, py in inp:
                blk['conn'][pname] = None
        
    for netname, conns in resolved.items():
        for conn in conns:
            for p in ['p0', 'p1']:
                if p in conn.d:
                    blkname, pname = conn.d[p]
                    blk = blocks[blkname]
                    blk['conn'][pname] = conn.netname
        

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
        if netname in portnames:
            external_nets[netname] = prop
        else:
            internal_nets[netname] = prop
    
    return blocks, internal_nets, external_nets
#        
#    
#    propertyList = []
#        
#    for p in properties.keys():
#        if p != 'name':
#            propertyList.append('{k}="{value}"'.format(k=p,value=properties[p]))
#    
#    params = ','.join(pinList + propertyList)
#    
#    #variables
#    user = subprocess.check_output("whoami").strip()
#    
#    impL = []
#    
#    for b in blocks:
#        string = "from " + "libraries import library_" + b['libname']
#        if not string in impL:
#            impL.append(string)
#    
#    imp = "\n".join(list(set(impL)))
#    
#    
#    signals = getSignals(connections,nodes)
#    
#    if signals == False:
#        return False
#    
#    signalL = []
#    for i in range(len(signals)):
#        if 'label' in signals[i]:
#            connName = signals[i]['label']
#            stop = False
#            for pin in pins:
#                if pin[0] == connName:
#                    stop = True
#            if stop:
#                continue
#        else:
#            connName = 'signal' + str(i + 1)
#        if 'type' in signals[i]:
#            type = signals[i]['type']
#        else:
#            type = '0'
#        string = connName + " = Signal({})".format(type)
#        signalL.append(string)
#       
#    signalsOutput = "\n    ".join(signalL)
#    
#    instanceL = []
#    signals
#    for b in blocks:
#        bname = b['blockname']
#        libname = b['libname']
#        instanceName = b['name']
#        
#        signalL = []
#        propertiesL = []
#        parameterList = []
#        
#        #print(getPins(b['libname'],b['blockname']),b['blockname'])
#        if 'parameters' in b:
#            pins = getPins(b['libname'],b['blockname'],b['parameters'])
#            for parameter in b['parameters'].keys():
#                parameterList.append('{} = "{}"'.format(parameter,b['parameters'][parameter]))
#        else:
#            pins = getPins(b['libname'],b['blockname'])
#        for pin in pins:
#            pos = dict(y=pin[2]+b['pos']['y'],x=pin[1]+b['pos']['x'])
#            for sindex,signal in enumerate(signals):
#                if pos in signal['posList']:
#                    if 'label' in signal:
#                        s = signal['label']
#                        break
#                    else:
#                        s = 'signal'+str(sindex + 1)
#                        break
#            else:
#                s = 'None'
#            signalL.append(pin[0] + '=' + s)
#            
#        for propertie in b['properties'].keys():
#            if propertie != 'name':
#                propertiesL.append('{} = "{}"'.format(propertie,b['properties'][propertie]))
#        
#        string = "{instanceName} = library_{libname}.{blockname}_myhdl({signals})"
#        
#        signalsOut = ",".join(signalL + propertiesL + parameterList)
#        instanceL.append(string.format(instanceName=instanceName,blockname=bname,libname=libname,signals=signalsOut))
#        
#    
#    instances = "\n    ".join(instanceL)
##    instances = str(signals)
#    
#    tbText = "pass"
    
    return template.format(projectname=projectname,
                           user=user,
                           blockname=blockname,
                           imp=imp,
                           params=params,
                           signals=signalsOutput,
                           instances=instances,
                           tbText=tbText,
                           copyrightText=copyrightText,
                           copyrightPolicy=copyrightPolicy)

def getPins(libname,blockname,param=dict()):
    block = libraries.getBlock(libname, blockname, None, None, param)
    block.setup(False)
    pins = []
    for inp in block.pins()[0]:
        name = inp[3]
        xpos = inp[1]
        ypos = inp[2]
        pins.append((name,xpos,ypos))
    for output in block.pins()[1]:
        name = output[3]
        xpos = output[1]
        ypos = output[2]
        pins.append((name,xpos,ypos))
    print(block.pins(),pins)
    return pins

def getSignals(connections,nodes):
    #signals = [signal1:[pos1,pos2],signal2:[pos1,pos2]]
    signals = []
    for conn in connections:
        for sindex,s in enumerate(signals):
            #check if signal exist and extends it
            for pindex,pos in enumerate(s):
                if pos['pos'] == conn['pos1']:
                    signals[sindex][pindex]['stay'] = False #make connection internal
                    signals[sindex].append(dict(pos=conn['pos2'],stay=True)) #expand connection
                    break
                if pos['pos'] == conn['pos2']:
                    signals[sindex][pindex]['stay'] = False #make connection internal
                    signals[sindex].append(dict(pos=conn['pos1'],stay=True)) #expand connection
                    break
            else:
                continue
            break
        else:
            #create new signal
            signals.append([dict(pos=conn['pos1'],stay=True),dict(pos=conn['pos2'],stay=True)])
    
    #merge 2 signals if they should be connected
    
    counter = 0
    while(counter < len(signals)):
        for pindex,pos in enumerate(signals[counter]):
            for sindex2,s2 in enumerate(signals):
                for pos2 in s2:
                    if (pos['pos'] == pos2['pos'] or getNodeLabel(pos['pos'],nodes) and getNodeLabel(pos['pos'],nodes) == getNodeLabel(pos2['pos'],nodes)) and counter != sindex2:
                        signals.remove(s2)
                        s2.remove(pos2)
#                        if sindex2 < counter:
#                            counter += 1
                        signals[counter][pindex]['stay'] = False
                        signals[counter] += s2
                        counter = 0
                        break
                else:
                    continue
                break
            else:
                continue
            break
        counter += 1
                        
   
    
    
    #remove all internal connections        
    outputSignals = []
    for sindex,s in enumerate(signals):
        posList = []
        for pos in s:
            if pos['stay']:
                posList.append(pos['pos'])
        if posList:
            signal = dict(posList=posList)
            label = getLabel(s,connections,nodes,'label')
            signaltype = getLabel(s,connections,nodes,'signalType')
            if label == False:
                return False
            elif label:
                signal['label'] = label
            if signaltype:
                signal['type'] = signaltype
            outputSignals.append(signal)
            
    
                    
        
    return outputSignals
    
def getNodeLabel(pos,nodes):
    for n in nodes:
        if n['pos'] == pos and 'label' in n:
            return n['label']
    return False            
    
def getLabel(signal,connections,nodes,key):
    labels = []
    for s in signal:
        for node in nodes:
            if s['pos'] == node['pos']:
                if key in node:
                    labels.append(node[key].replace(' ','_'))
        for conn in connections:
            if s['pos'] == conn['pos1'] or s['pos'] == conn['pos2']:
                if key in conn:
                    labels.append(conn[key].replace(' ','_'))
    if len(labels) == 1:
        return labels[0]
    elif len(labels) == 0:
        return None
    else:
        return False
    
        
    
if __name__ == "__main__":
    lang = 'myhdl'
#    fname = os.path.join(d, 'saves', 'untitled.py')
    fname = os.path.join(d, 'saves', 'sailpll.py')
    nldir = os.path.join(const.netlist_dir + '_' + lang, strip_ext(os.path.basename(fname), '.py'))
    netlist(fname, netlist_dir=nldir)
    print('done')