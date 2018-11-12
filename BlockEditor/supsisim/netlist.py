
from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

import os, sys
from collections import OrderedDict

d = os.path.dirname(os.path.dirname(__file__))
sys.path.append(d)

import subprocess
from   supsisim.const import viewTypes,copyrightText,copyrightPolicy,projectname
from   supsisim.src_import import import_module_from_source_file
import libraries

filenameTemplate = 'libraries.library_{}.{}'

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

def netlist(filename, properties=dict(), lang='myhdl'):
    d, module_name = os.path.split(filename)
    ed, ext = viewTypes['diagram']
    module_name = module_name.rstrip(ext)

    blocks, internal_nets, external_nets = resolve_connectivity(filename, properties=dict())

    if lang == 'myhdl':
        return toMyhdl(module_name, blocks, internal_nets, external_nets)

def defaultMyHdlInstance(name, libname, blockname, connectDict):
    conns = []
    for pinname,netname in connectDict.items():
        conns.append('{} = {}'.format(pinname, netname))
    jj = ',\n' + ' ' * 16
    c = jj.join(conns)
    return 'u_{} = {}.{}({})\n'.format(name, libname, blockname, c)

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

    ret = ['#netlist of {}\n'.format(module_name)]
    ret.append('from myhdl import block, Signal, intbv, fixbv, instances\n')
    
    # imports
    imports = set()
    for name, blk in blocks.items():
        imports.add(blk['libname'])
    
    
    for lib in imports:
        ret.append('import {}'.format(lib))
    ret.append('')
    
    # block definition
    ret.append('@block\ndef {}({}):'.format(module_name, ', '.join(external_nets)))
    ret.append('')

    # internal_nets
    ret.append('    # internal nets')
    for netname in internal_nets:
        tp = internal_nets[netname]['signalType']
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

    block_modules = dict()
    for name, blk in blocks.items():
        blockname, libname = blk['blockname'],  blk['libname']
        fname = libraries.blockpath(libname, blockname)
        block_modules[blockname+'/'+libname] = import_module_from_source_file(fname)

    portnames = set()            
    nodes = dict()
    for n in dgm.nodes:
        xy  = n['x'], n['y']
        nodes[xy] = NetObj(n)
        if 'label' in n and n['porttype'] != 'node':
            portnames.add(n['label']['text'])

#    pins = dict()
#    for k in nodes.keys():
#        if nodes[k]['porttype'] != 'node':
#            pins[k] = nodes.pop(k)
    


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
    n_nets = 0 # used to number anonymous nets
    while unresolved:
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
        block_module = block_modules[blockname+'/'+libname]
        
        inp, outp = block_module.inp, block_module.outp
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
    mynetlist = netlist(os.path.join(d, 'saves', 'sailpll.py'))
    print(mynetlist)