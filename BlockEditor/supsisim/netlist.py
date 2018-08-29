import subprocess
from supsisim.const import PD,PW,BWmin,copyrightText,copyrightPolicy,projectname

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


def netlist(blockname,libname,properties):
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
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
        string = "from " + "libraries.library_" + b['libname'] + ' import ' + b['blockname'] + "_myhdl as " + b['blockname']
        if not string in impL:
            impL.append(string)
    
    imp = "\n".join(impL)
    
    
    signals = getSignals(connections,nodes)
    print(signals)    
    
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
    
    for b in blocks:
        bname = b['blockname']
        if b['name'] == bname:
            instanceName = bname + "0"
        else:
            instanceName = b['name']
        
        signalL = []
        
        for pin in getPins(b['libname'],b['blockname']):
            pos = dict(y=pin[2]+b['pos']['y'],x=pin[1]+b['pos']['x'])
            for sindex,signal in enumerate(signals):
                if pos in signal['posList']:
                    if 'label' in signal:
                        signalL.append(signal['label'])
                    else:
                        signalL.append('signal'+str(sindex + 1))
        
        string = "{instanceName} = {blockname}({signals})"
        
        signalsOut = ",".join(signalL)
        instanceL.append(string.format(instanceName=instanceName,blockname=bname,signals=signalsOut))
        
    
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

def getPins(libname,blockname):
    fname = filenameTemplate.format(libname,blockname)
    exec('import ' + fname)
    reload(eval(fname))
    pins = []
    inp = eval(fname + '.inp')
    outp = eval(fname + '.outp')
    
    if isinstance(inp,int):
        for n in range(inp):
            ypos = -PD*(inp-1)/2 + n*PD
            xpos = -(BWmin+PW)/2
            name = 'dummy'
            pins.append((name,xpos,ypos))
    else:
        pins += inp
        
    if isinstance(outp,int):  
        for n in range(outp):
            ypos = -PD*(outp-1)/2 + n*PD
            xpos = (BWmin+PW)/2
            name = 'dummy'
            pins.append((name,xpos,ypos))
    else:
        pins += outp
    
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
                    if pos['pos'] == pos2['pos'] and counter != sindex2:
                        signals.remove(s2)
                        s2.remove(pos2)
#                        if sindex2 < counter:
#                            counter += 1
                        print(len(signals),counter)
                        print(len(signals[counter]),pindex)
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
            if label:
                signal['label'] = label
            if signaltype:
                signal['type'] = signaltype
            outputSignals.append(signal)
            
    
                    
        
    return outputSignals
    

def getLabel(signal,connections,nodes,key):
    for s in signal:
        for node in nodes:
            if s['pos'] == node['pos']:
                if key in node:
                    return node[key].replace(' ','_')
        for conn in connections:
            if s['pos'] == conn['pos1'] or s['pos'] == conn['pos2']:
                if key in conn:
                    return conn[key].replace(' ','_')
    
if __name__ == "__main__":
    print(netlist('testSymbol'))