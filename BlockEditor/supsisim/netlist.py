import subprocess
from supsisim.const import PD,PW,BWmin,copyrightText,copyrightPolicy,projectname
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


def netlistMyHdl(blockname,libname,properties):
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    #import all items
    fname = filenameTemplate.format(libname,blockname) + "_diagram"
    
    exec('import ' + fname)
    reload(eval(fname))
    
    blocks = eval(fname + '.blocks')
    connections = eval(fname + '.connections')
    nodes = eval(fname + '.nodes')
    
    #import attributes
    
    
    pins = getPins(libname,blockname)
    
    pinList = []    
    for p in pins:
       pinList.append(p[0]) 
    
    
    propertieList = []
        
    for p in properties.keys():
        if p != 'name':
            propertieList.append('{k}="{value}"'.format(k=p,value=properties[p]))
    
    params = ','.join(pinList + propertieList)
    
    #variables
    user = subprocess.check_output("whoami").strip()
    
    impL = []
    
    for b in blocks:
        string = "from " + "libraries import library_" + b['libname']
        if not string in impL:
            impL.append(string)
    
    imp = "\n".join(list(set(impL)))
    
    
    signals = getSignals(connections,nodes)
    
    if signals == False:
        return False
    
    signalL = []
    for i in range(len(signals)):
        if 'label' in signals[i]:
            connName = signals[i]['label']
            stop = False
            for pin in pins:
                if pin[0] == connName:
                    stop = True
            if stop:
                continue
        else:
            connName = 'signal' + str(i + 1)
        if 'type' in signals[i]:
            type = signals[i]['type']
        else:
            type = '0'
        string = connName + " = Signal({})".format(type)
        signalL.append(string)
       
    signalsOutput = "\n    ".join(signalL)
    
    instanceL = []
    signals
    for b in blocks:
        bname = b['blockname']
        libname = b['libname']
        instanceName = b['name']
        
        signalL = []
        propertiesL = []
        parameterList = []
        
        #print(getPins(b['libname'],b['blockname']),b['blockname'])
        if 'parameters' in b:
            pins = getPins(b['libname'],b['blockname'],b['parameters'])
            for parameter in b['parameters'].keys():
                parameterList.append('{} = "{}"'.format(parameter,b['parameters'][parameter]))
        else:
            pins = getPins(b['libname'],b['blockname'])
        for pin in pins:
            pos = dict(y=pin[2]+b['pos']['y'],x=pin[1]+b['pos']['x'])
            for sindex,signal in enumerate(signals):
                if pos in signal['posList']:
                    if 'label' in signal:
                        s = signal['label']
                        break
                    else:
                        s = 'signal'+str(sindex + 1)
                        break
            else:
                s = 'None'
            signalL.append(pin[0] + '=' + s)
            
        for propertie in b['properties'].keys():
            if propertie != 'name':
                propertiesL.append('{} = "{}"'.format(propertie,b['properties'][propertie]))
        
        string = "{instanceName} = library_{libname}.{blockname}_myhdl({signals})"
        
        signalsOut = ",".join(signalL + propertiesL + parameterList)
        instanceL.append(string.format(instanceName=instanceName,blockname=bname,libname=libname,signals=signalsOut))
        
    
    instances = "\n    ".join(instanceL)
#    instances = str(signals)
    
    tbText = "pass"
    
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
    block = libraries.getBlock(blockname, libname, None, None, param)
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
#    fname = filenameTemplate.format(libname,blockname)
#    exec('import ' + fname)
#    reload(eval(fname))
#    pins = []
#    inp = eval(fname + '.inp')
#    outp = eval(fname + '.outp')
#    
#    if isinstance(inp,int):
#        for n in range(inp):
#            ypos = -PD*(inp-1)/2 + n*PD
#            xpos = -(BWmin+PW)/2
#            name = None
#            pins.append((name,xpos,ypos))
#    else:
#        pins += inp
#        
#    if isinstance(outp,int):  
#        for n in range(outp):
#            ypos = -PD*(outp-1)/2 + n*PD
#            xpos = (BWmin+PW)/2
#            name = None
#            pins.append((name,xpos,ypos))
#    else:
#        pins += outp
#    
#    return pins

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
    print(netlist('testSymbol'))