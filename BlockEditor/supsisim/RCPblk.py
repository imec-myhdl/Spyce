"""
This is a procedural interface to the RCPblk library

roberto.bucher@supsi.ch

The following class is provided:

  RCPblk      - class with info for Rapid Controller Prototyping

The following commands are provided:

  stepBlk        - Create STEP block 
  sineBlk        - Create SINUS block 
  squareBlk      - Create SQUARE block 
  printBlk       - Create PRINT block 
  sumBlk         - Create SUM block 
  saturBlk       - Create SATURATION block 
  dssBlk         - Create DSS block (discrete state space)
  cssBlk         - Create CSS block (continous state space)
  matmultBlk     - Create MXMULT block
  constBlk       - Create CONST block
  absBlk         - Create ABS block
  prodBlk        - Create PROD block
  extdataBlk     - Create EXTDATA input block
  epos_MotIBlk   - Create EPOS_MOTI block
  epos_MotXBlk   - Create EPOS_MOTX block
  epos_EncBlk    - Create EPOS ENC block
  maxon_MotBlk   - Create MAXON_MOTI block
  maxon_EncBlk   - Create MAXON ENC block
  epos_areadBlk  - Create EPOS ANALOG READ block
  init encBlk    - Initialize outputs
  rtxmlServerBlk - RTXML Server for data browsing
  rtxmlSigInBlk  - RTXML for input signal
  rtxmlSigOutBlk - RTXML for output signal
  comediADBlk    - Comedi Analog to Digital
  comediDABlk    - Comedi Digital to Analog
  comediDIBlk    - Comedi digital input
  comediDOBlk    - Comedi digital output
  baumer_encBlk  - Create BAUMER ENC block
  switchBlk      - Switch Block
  lutBlk         - Look Up Table Block
  intgBlk        - Integral Block
  zdelayBlk      - Unit delay Block
  unixsocketCBlk - Socket Unix Block - Client
  unixsocketSBlk - Socket Unix Block - Server
  MCLM_MotXBlk   - Create FAULHABER_MOTI block
  MCLM_EncBlk    - Create FAULHABER ENC block
  MCLM_ADBlk     - Create FAULHABER AD block
  FmuBlk         - Create an interface to a FMU element
  FmuInBlk       - Create an interface to a FMU element
  genericBlk     - Create an interface to a generic C function
  init_maxon_MotBlk     - Initialize a Maxon CAN device
  init_epos_MotIBlk     - Initialize an Epos CAN device for torque control
  can_sdo_sendBlk     - Send a standard can message
  can_sdo_sendThBlk   - Send a standard can message
  can_sdo_recvBlk     - Receive a standard can message
  can_gen_recvBlk     - Receive a generic can message
  
"""
from builtins import str
from builtins import range
from builtins import object
from control import *
from scipy import mat, shape, size, array, zeros
from numpy import reshape, hstack

class RCPblk(object):
    def __init__(self, *args):  
        if len(args) == 8:
            (fcn,pin,pout,nx,uy,realPar,intPar,str) = args
        elif len(args) == 7:
            (fcn,pin,pout,nx,uy,realPar,intPar) = args
            str=''
        else:
            raise ValueError("Needs 6 or 7 arguments; received %i." % len(args))
        
        self.fcn = fcn
        self.pin = array(pin)
        self.pout = array(pout)
        self.nx = array(nx)
        self.uy = array(uy)
        self.realPar = array(realPar)
        self.intPar = array(intPar)
        self.str = str

    def __str__(self):
        """String representation of the Block"""
        str =  "Function           : " + self.fcn.__str__() + "\n"
        str += "Input ports        : " + self.pin.__str__() + "\n"
        str += "Output ports      : " + self.pout.__str__() + "\n"
        str += "Nr. of states      : " + self.nx.__str__() + "\n"
        str += "Relation u->y      : " + self.uy.__str__() + "\n"
        str += "Real parameters    : " + self.realPar.__str__() + "\n"
        str += "Integer parameters : " + self.intPar.__str__() + "\n"
        str += "String Parameter   : " + self.str.__str__() + "\n"
        return str

def stepBlk(pout, initTime, Val):
    """Create STEP block 

    Step input signal

    Call: stepBlk(pout, initTime, Val)

    Parameters
    ----------
    pout : connected output port
    initTime: step Time
    Val : Value at step Time

    Returns
    -------
    blk  : RCPblk
"""

    if(size(pout) != 1):
        raise ValueError("Block should have 1 output port; received %i." % size(pout))
    blk = RCPblk('step',[],pout,[0,0],0,[initTime, Val],[])
    return blk

def sineBlk(pout, Amp, Freq, Phase, Bias, Delay):
    """Create SINUS block 

    Sine input dignal

    Call: sineBlk(pout, Amp, Freq, Phase, Bias, Delay)

    Parameters
    ----------
    pout : connected output port
    Amp: Signal Amplitude
    Freq: Signal Freq
    Phase: Signale Phase
    Bias: Signal Bias
    Delay: Signal Delay

    Returns
    -------
    blk  : RCPblk
"""

    if(size(pout) != 1):
        raise ValueError("Block should have 1 output port; received %i." % size(pout))
    blk = RCPblk('sinus', [],pout,[0,0],0,[Amp, Freq, Phase, Bias, Delay],[])
    return blk

def squareBlk(pout, Amp, Period, Width, Bias, Delay):
    """Create SQUARE block 

    Square input signal
    
    Call: squareBlk(pout, Amp, Period, Width, Bias, Delay)

    Parameters
    ----------
    pout : connected output port
    Amp: Signal Amplitude
    Period: Signal Perios
    Width: Signale Width
    Bias: Signal Bias
    Delay: Signal Delay

    Returns
    -------
    blk  : RCPblk
"""

    if(size(pout) != 1):
        raise ValueError("Block should have 1 output port; received %i." % size(pout))
    blk = RCPblk('square',[],pout,[0,0],0,[Amp, Period, Width, Bias, Delay],[])
    return blk

def printBlk(pin):
    """Create PRINT block 

    Print output data
    
    Call: printBlk(pin)

    Parameters
    ----------
    pin : connected input ports

    Returns
    -------
    blk  : RCPblk
"""

    blk = RCPblk('print',pin,[],[0,0],1,[],[])
    return blk

def sumBlk(pin, pout, Gains):
    """Create SUM block 

    Saturation of the input signal

    Call: sumBlk(pin,pout, Gains)

    Parameters
    ----------
    pin : connected input ports
    pout: connected output port
    Gains: input gains

    Returns
    -------
    blk  : RCPblk
"""
    if(size(pin) != size(Gains)):
        raise ValueError("Number of inputs (%i) should match Gain Size (%i)" % (size(pin),size(Gains)))
    if(size(pout) != 1):
        raise ValueError("Block should have 1 output port; received %i." % size(pout))

    blk = RCPblk('sum',pin,pout,[0,0],1,Gains,[])
    return blk

def saturBlk(pin,pout,satP, satN):
    """Create SATURATION block 

    Call: saturBlk(pin,pout, satP, satN)

    Parameters
    ----------
    pin : connected input ports
    pout: connected output ports
    satP: Upper saturation
    satN: Lower saturation

    Returns
    -------
    blk  : RCPblk
"""
    if(size(pin) != 1):
        raise ValueError("Block should have 1 input port; received %i." % size(pin))
    if(size(pout) != 1):
        raise ValueError("Block should have 1 output port; received %i." % size(pout))
    blk = RCPblk('saturation',pin,pout,[0,0],1,[satP, satN],[])
    return blk

def dssBlk(pin,pout,sys,X0=[]):
    """Create DSS block 

    Discrete state space block

    Call: dssBlk(pin,pout, sys,X0)

    Parameters
    ----------
    pin : connected input ports
    pout: connected output ports
    sys: Discrete system in SS form
    X0: Initial conditions

    Returns
    -------
    blk  : RCPblk
"""
    if isinstance(sys, TransferFunction):
        sys=tf2ss(sys)

    nin = size(pin)
    ni = shape(sys.B)[1];
    if (nin != ni):
        raise ValueError("Block have %i inputs: received %i input ports" % (nin,ni))
    
    no = shape(sys.C)[0]
    nout = size(pout)
    if(no != nout):
        raise ValueError("Block have %i outputs: received %i output ports" % (nout,no))
        
    a  = reshape(sys.A,(1,size(sys.A)),'C')
    b  = reshape(sys.B,(1,size(sys.B)),'C')
    c  = reshape(sys.C,(1,size(sys.C)),'C')
    d  = reshape(sys.D,(1,size(sys.D)),'C')
    nx = shape(sys.A)[0]

    if(size(X0) == nx):
        X0 = reshape(X0,(1,size(X0)),'C')
    else:
        X0 = mat(zeros((1,nx)))

    indA = 0
    indB = nx*nx
    indC =indB + nx*ni
    indD = indC + nx*no
    indX = indD + ni*no
    intPar = [nx,ni,no,indA, indB, indC, indD, indX]
    realPar = hstack((a,b,c,d,X0))

    if d.any() == True:
        uy = 1
    else:
        uy = 0
    
    blk = RCPblk('dss',pin,pout,[0,nx],uy,realPar,intPar)
    return blk

def cssBlk(pin,pout,sys,X0=[]):
    """Create CSS block 

    Continous state space block

    Call: cssBlk(pin,pout, sys,X0)

    Parameters
    ----------
    pin : connected input ports
    pout: connected output ports
    sys: Discrete system in SS form
    X0: Initial conditions

    Returns
    -------
    blk  : RCPblk
"""
    if isinstance(sys, TransferFunction):
        sys=tf2ss(sys)

    nin = size(pin)
    ni = shape(sys.B)[1];
    if (nin != ni):
        raise ValueError("Block have %i inputs: received %i input ports" % (nin,ni))
    
    no = shape(sys.C)[0]
    nout = size(pout)
    if(no != nout):
        raise ValueError("Block have %i outputs: received %i output ports" % (nout,no))
        
    a  = reshape(sys.A,(1,size(sys.A)),'C')
    b  = reshape(sys.B,(1,size(sys.B)),'C')
    c  = reshape(sys.C,(1,size(sys.C)),'C')
    d  = reshape(sys.D,(1,size(sys.D)),'C')
    nx = shape(sys.A)[0]

    if(size(X0) == nx):
        X0 = reshape(X0,(1,size(X0)),'C')
    else:
        X0 = mat(zeros((1,nx)))

    indA = 1
    indB = indA + nx*nx
    indC = indB + nx*ni
    indD = indC + nx*no
    indX = indD + ni*no
    intPar = [nx,ni,no, indA, indB, indC, indD, indX]
    realPar = hstack((mat([0.0]),a,b,c,d,X0))

    if d.any() == True:
        uy = 1
    else:
        uy = 0
    
    blk = RCPblk('css',pin,pout,[nx,0],uy,realPar,intPar)
    return blk

def matmultBlk(pin,pout,Gains):
    """Create MXMULT block 

    Matrix multiplication of the input signals
    
    Call: matmultBlk(pin,pout, Gains)

    Parameters
    ----------
    pin : connected input ports
    pout: connected output ports
    Gains : Matrix with gains

    Returns
    -------
    blk  : RCPblk
"""
    Gains = mat(Gains)
    n,m = shape(Gains)
    if(size(pin) != m):
        raise ValueError("Block should have %i input port; received %i." % (m,size(pin)))
    if(size(pout) != n):
        raise ValueError("Block should have %i output port; received %i." % (n,size(pout)))
    realPar  = reshape(Gains,(1,size(Gains)),'C')
    blk = RCPblk('mxmult',pin,pout,[0,0],1,realPar,[n,m])
    return blk

def constBlk(pout,val):
    """Create CONST block 

    Constant value as input

    Call: constBlk(pout, val)

    Parameters
    ----------
    pout: connected output ports
    val: Const. Value

    Returns
    -------
    blk  : RCPblk
"""
    if(size(pout) != 1):
        raise ValueError("Block should have 1 output port; received %i." % size(pout))
    blk = RCPblk('constant',[],pout,[0,0],0,[val],[])
    return blk

def absBlk(pin,pout):
    """Create ABS block 

    Absolute Value of the input signal
    
    Call: absBlk(pin,pout)

    Parameters
    ----------
    pin : connected input ports
    pout: connected output ports

    Returns
    -------
    blk  : RCPblk
"""
    if(size(pout) != size(pin)):
        raise ValueError("Block should have same input and output port sizes; received %i %i." % (size(pin),size(pout)))
    blk = RCPblk('absV',pin,pout,[0,0],1,[],[])
    return blk

def prodBlk(pin, pout):
    """Create PROD block 

    Multiply input signals
    
    Call: prodBlk(pin,pout)

    Parameters
    ----------
    pin : connected input ports
    pout: connected output port

    Returns
    -------
    blk  : RCPblk
"""
    if(size(pout) != 1):
        raise ValueError("Block should have 1 output port; received %i." % size(pout))

    blk = RCPblk('prod',pin,pout,[0,0],1,[],[])
    return blk

def extdataBlk(pout, length, fname):
    """Create EXTDATA block 

    Get input data from an external file
    
    Call: extdataBlk(pout, length, fname)

    Parameters
    ----------
    pout: connected output port
    length: number of points in file
    fname: Filename with data

    Returns
    -------
    blk  : RCPblk
"""
    if(size(pout) != 1):
        raise ValueError("Block should have 1 output port; received %i." % size(pout))

    blk = RCPblk('extdata',[],pout,[0,0],0,[],[length,0],fname)
    return blk

def epos_MotIBlk(pin, ID, propGain, intGain):
    """Create EPOS_MOTI block 

    Get input data from an external file
    
    Call: epos_MotIBlk(pin, ID, PropGain, IntgGain)

    Parameters
    ----------
    pin: connected input port
    ID: CAN node ID
    PropGain: Proportional gain of the epos torque controller
    IntgGain: Integral gain of the epos torque controller

    Returns
    -------
    blk  : RCPblk
"""
    if(size(pin) != 1):
        raise ValueError("Block should have 1 input port; received %i." % size(pout))

    blk = RCPblk('epos_canopen_motI',pin,[],[0,0],1,[propGain, intGain],[ID])
    return blk

def epos_MotXBlk(pin, ID, propGain, intGain, derGain, Vff, Aff):
    """Create EPOS_MOTI block 

    Get input data from an external file
    
    Call: epos_MotXBlk(pin, ID, propGain, intgGain, derGain, Vff, Aff)

    Parameters
    ----------
    pin: connected input port
    ID: CAN node ID
    propGain: Proportional gain of the epos position controller
    intgGain: Integral gain of the epos position controller
    derGain:  Derivative gain of the epos position controller
    Vff    : Velocity Fedd Forward Factor
    Aff    : Acceleration Feed Forward Factor

    Returns
    -------
    blk  : RCPblk
"""
    if(size(pin) != 1):
        raise ValueError("Block should have 1 input port; received %i." % size(pout))

    blk = RCPblk('epos_canopen_motX',pin,[],[0,0],1,[propGain, intGain, derGain, Vff, Aff],[ID])
    return blk

def epos_EncBlk(pout, ID, res):
    """Create EPOS_ENC block 

    Get encoder value from an maxon epos driver

    Call: epos_EncBlk(pout, ID, res)

    Parameters
    ----------
    pout: connected output port
    ID: CAN node ID
    res: encoder resolution

    Returns
    -------
    blk  : RCPblk
"""
    if(size(pout) != 1):
        raise ValueError("Block should have 1 output port; received %i." % size(pout))

    blk = RCPblk('epos_canopen_enc',[],pout,[0,0],0,[4*res],[ID])
    return blk

def maxon_MotBlk(pin, ID, propGain, intGain):
    """Create MAXON_MOT block 

    Maxon driver for torque control

    Call: maxon_MotBlk(pin, ID)

    Parameters
    ----------
    pin: connected input port
    ID: CAN node ID

    Returns
    -------
    blk  : RCPblk
"""
    if(size(pin) != 1):
        raise ValueError("Block should have 1 input port; received %i." % size(pout))

    blk = RCPblk('maxon_mot',pin,[],[0,0],1,[propGain, intGain],[ID])
    return blk

def maxon_EncBlk(pout, ID, res):
    """Create MAXON_ENC block 

    Maxon driver for encoder

    Call: maxon_EncBlk(pout, ID, res)

    Parameters
    ----------
    pout: connected output port
    ID: CAN node ID
    res: encoder resolution

    Returns
    -------
    blk  : RCPblk
"""
    if(size(pout) != 1):
        raise ValueError("Block should have 1 output port; received %i." % size(pout))

    blk = RCPblk('maxon_enc',[],pout,[0,0],0,[4*res],[ID])
    return blk

def epos_areadBlk(pout, ID, ch):
    """Create EPOS_ANALOG READ block 

    Get analog value from an maxon epos driver

    Call: epos_areadBlk(pout, ID, ch)

    Parameters
    ----------
    pout: connected output port
    ID: CAN node ID
    ch : Analog input channel

    Returns
    -------
    blk  : RCPblk
"""
    if(size(pout) != 1):
        raise ValueError("Block should have 1 output port; received %i." % size(pout))

    blk = RCPblk('epos_canopen_aread',[],pout,[0,0],0,[],[ID, ch])
    return blk

def init_encBlk(pin, pout, trgtime, defv, offset):
    """Create INIT OUTPUT block 

    Initialize the output of a block to a given value

    Call: init_encBlk(pin, pout, trgtime, defv, offset)

    Parameters
    ----------
    pin: connected input port
    pout: connected output port
    trgtime: time to fix the output
    defv : default value up to trigger time
    offset: offset to add to the output

    Returns
    -------
    blk  : RCPblk
"""
    if (size(pout) != 1) or (size(pin) != 1):
        raise ValueError("Block should have 1 input and 1 output port; received %i and %i." % (size(pin),size(pout)))

    blk = RCPblk('init_enc',pin,pout,[0,0],1,[trgtime, defv, offset, 0.0],[])
    return blk

def rtxmlServerBlk(P1, P2, P3, Par, port):
    """Create RTXMLSERVER block 

    Initialize the rtxml http server

    Call: rtxmlserverBlk(P1, P2, P3, Par, port)

    Parameters
    ----------
    P1   : list of Signals for Plot 1
    P2   : list of Signals for Plot 2
    P3   : list of Signals for Plot 3
    Par  : Additional parameters
    port : HTTP port

        Returns
    -------
    blk  : RCPblk
"""
    xmlsettings = '<PLOT1>'
    plt = P1.split()
    for n in range(0,size(plt)):
        xmlsettings += '<SIGNAL' + str(n+1) + '>'+plt[n] + '</SIGNAL' + str(n+1) + '>'
    xmlsettings += '</PLOT1><PLOT2>'
    plt = P2.split()
    for n in range(0,size(plt)):
        xmlsettings += '<SIGNAL' + str(n+1) + '>'+plt[n] + '</SIGNAL' + str(n+1) + '>'
    xmlsettings += '</PLOT2><PLOT3>'
    plt = P3.split()
    for n in range(0,size(plt)):
        xmlsettings += '<SIGNAL' + str(n+1) + '>'+plt[n] + '</SIGNAL' + str(n+1) + '>'
    xmlsettings += '</PLOT3>'
    xmlsettings += Par
        
    blk = RCPblk('rtxmlserver_fnc',[],[],[0,0],0,[],[3140,port],xmlsettings)
    return blk

def rtxmlSigInBlk(pout, Sig, defV):
    """Create XML SIGNAL block 

    Block to send signals to HTTP server

    Call: rtxmlSigInBlk(pin, Sig, DefV)

    Parameters
    ----------
    pin: connected input port
    Sig: Signal name
    DefV: Default Value

    Returns
    -------
    blk  : RCPblk
"""
    if size(pout) != 1:
        raise ValueError("Block should have 1 input port; received %i !" % size(pin))

    blk = RCPblk('rtxmlsignal_fnc',[],pout,[0,0],0,[defV],[0],Sig)
    return blk

def rtxmlSigOutBlk(pin, Sig, defV):
    """Create XML SIGNAL block 

    Block to send signals to HTTP server

    Call: rtxmlSigOutBlk(pin, Sig)

    Parameters
    ----------
    pin: connected input port
    Sig: Signal name
    DefV: Default Value

    Returns
    -------
    blk  : RCPblk
"""
    if size(pin) != 1:
        raise ValueError("Block should have 1 input port; received %i !" % size(pin))

    blk = RCPblk('rtxmlsignal_fnc',pin,[],[0,0],1,[defV],[1],Sig)
    return blk

def comediADBlk(pout, dev, ch, cr):
    """Create Comedi Analog to Digital block
    Call: comediADBlk(pout,dev,ch,range,ref)

    Parameters
    ----------
    pout   -  output pin 
    dev    -  Comedi device
    ch     -  Channel
    cr     -  analog range
    
    Returns
    -------
    blk  : RCPblk
"""
    if size(pout) != 1:
        raise ValueError("Block should have 1 input port; received %i !" % size(pout))

    blk = RCPblk('comedi_analog_input',[],pout,[0,0],0,[],[ch, cr],dev)
    return blk

def comediDABlk(pin, dev, ch, cr):
    """Create Comedi Digital to Analog block
    Call: comediDABlk(pin, dev,ch,range,ref)

    Parameters
    ----------
    pin    -  input pin
    dev    -  Comedi device
    ch     -  Channel
    cr     -  analog range
    
    Returns
    -------
    blk  : RCPblk
"""
    if size(pin) != 1:
        raise ValueError("Block should have 1 input port; received %i !" % size(pin))

    blk = RCPblk('comedi_analog_output',pin,[],[0,0],1,[],[ch, cr],dev)
    return blk

def comediDIBlk(pout, dev, ch):
    """Create Comedi Digital Input block
    Call: comediDIBlk(pout, dev,ch)

    Parameters
    ----------
    pout   -  output pin 
    dev    -  Comedi device
    ch     -  Channel
    
    Returns
    -------
    blk  : RCPblk
"""
    if size(pout) != 1:
        raise ValueError("Block should have 1 input port; received %i !" % size(pout))

    blk = RCPblk('comedi_digital_input',[],pout,[0,0],0,[],[ch],dev)
    return blk

def comediDOBlk(pin, dev, ch, thr):
    """Create Comedi Digital Output block
    Call: comediDOBlk(pin,dev,ch)

    Parameters
    ----------
    pin    -  Input pin
    dev    -  Comedi device
    ch     -  Channel
    
    Returns
    -------
    blk  : RCPblk
"""
    if size(pin) != 1:
        raise ValueError("Block should have 1 input port; received %i !" % size(pin))

    blk = RCPblk('comedi_digital_output',pin,[],[0,0],1,[thr],[ch],dev)
    return blk

def baumer_EncBlk(pout, ID, res):
    """Create BAUMER_ENC block 

    Maxon driver for encoder

    Call: baumer_EncBlk(pout, ID, res)

    Parameters
    ----------
    pout: connected output port
    ID: CAN node ID
    res: encoder resolution

    Returns
    -------
    blk  : RCPblk
"""
    if(size(pout) != 1):
        raise ValueError("Block should have 1 output port; received %i." % size(pout))

    blk = RCPblk('baumer_enc',[],pout,[0,0],0,[4*res],[ID])
    return blk

def switchBlk(pin,pout, cond, val, pers):
    """Create switch block 

    Call: switchBlk(pin, pout, cond, val, pers)

    Parameters
    ----------
    pin: connected input ports (3)
    pout: connected output port
    cond:  0 >, 1 <
    val:   value to compare
    pers:  switch can change again (0) or is fixed (1)

    Output switches from input 1 to input 2 if the condition is reached
    (input 3 > or <) than val;
    If pers is 1 the system doesn't switch back again if the condition is
    no more satisfied
    
    Returns
    -------
    blk  : RCPblk
"""
    if(size(pin) != 3):
        raise ValueError("Block should have 3 input ports; received %i." % size(pin))

    if(size(pout) != 1):
        raise ValueError("Block should have 1 output port; received %i." % size(pout))

    blk = RCPblk('switcher',pin,pout,[0,0],1,[val],[cond, pers])
    return blk

def lutBlk(pin, pout, coeff):
    """Create a Look Up Table block with polynomial curve 

    Call: lutBlk(pin, pout, coeff)

    Parameters
    ----------
    pin: connected input ports (3)
    pout: connected output port
    coeff:  polynomial coefficients
    
    Returns
    -------
    blk  : RCPblk
"""
    if(size(pin) != 1):
        raise ValueError("Block should 1 input port; received %i." % size(pin))

    if(size(pout) != 1):
        raise ValueError("Block should have 1 output port; received %i." % size(pout))

    blk = RCPblk('lut',pin,pout,[0,0],1,[coeff],[size(coeff)])
    return blk

def intgBlk(pin,pout,X0=0.0):
    """Create integral block 

    Continous integral block

    Call: intgBlk(pin,pout,X0)

    Parameters
    ----------
    pin : connected input port
    pout: connected output port
    X0: Initial conditions

    Returns
    -------
    blk  : RCPblk
"""
    nin = size(pin)
    if (nin != 1):
        raise ValueError("Block have 1 input: received %i input ports" % nin)
    
    nout = size(pout)
    if(nout != 1):
        raise ValueError("Block have 1 output1: received %i output ports" % nout)
        
    blk = RCPblk('integral',pin,pout,[1,0],0,[0.0 ,X0],[])
    return blk


def zdelayBlk(pin,pout,X0=0.0):
    """Create unit delay block 

    Continous integral block

    Call: zdelayBlk(pin,pout,X0)

    Parameters
    ----------
    pin : connected input port
    pout: connected output port
    X0: Initial conditions

    Returns
    -------
    blk  : RCPblk
"""
    nin = size(pin)
    if (nin != 1):
        raise ValueError("Block have 1 input: received %i input ports" % nin)
    
    nout = size(pout)
    if(nout != 1):
        raise ValueError("Block have 1 output1: received %i output ports" % nout)
        
    blk = RCPblk('unitDelay',pin,pout,[0,1],0,[X0],[])
    return blk

def trigBlk(pin,pout,tp):
    """Create trigonometric block 

    Trigonometric block

    Call: intgBlk(pin,pout,type sin=1 cos=2 tan=3)

    Parameters
    ----------
    pin : connected input port
    pout: connected output port
    type: Math function

    Returns
    -------
    blk  : RCPblk
"""
    nin = size(pin)
    if (nin != 1):
        raise ValueError("Block have 1 input: received %i input ports" % nin)
    
    nout = size(pout)
    if(nout != 1):
        raise ValueError("Block have 1 output1: received %i output ports" % nout)
        
    blk = RCPblk('trigo',pin,pout,[0,0],1,[],[tp])
    return blk

def unixsocketCBlk(pin,sockname):
    """Create Unix Socket block 

    Unix Socket block - Client

    Call: unixsocketBlk(pin,socketname)

    Parameters
    ----------
    pin : connected input port
    type: Socket name (string)

    Returns
    -------
    blk  : RCPblk
"""
    blk = RCPblk('unixsockC',pin,[],[0,0],1,[],[0],'/tmp/'+sockname)
    return blk

def unixsocketSBlk(pout,sockname,defvals):
    """Create Unix Socket block - Server 

    Unix Socket block

    Call: unixsocketBlk(pin,socketname)

    Parameters
    ----------
    pin      : connected input port
    type     : Socket name (string)
    defvals  : Default outputs

    Returns
    -------
    blk  : RCPblk
"""
    outputs = len(pout)
    vals = zeros(outputs,float)
    if len(defvals) > outputs:
        N=outputs
    else:
        N = len(defvals)

    for n in range(N):
        vals[n]=defvals[n]
        
    blk = RCPblk('unixsockS',[],pout,[0,0],0,defvals,[0,0],'/tmp/'+sockname)
    return blk

def MCLM_MotXBlk(pin, ID, res, kp, kd, zero):
    """Create MCLM_MOTX block 

    Get input data from an external file
    
    Call: MCLM_MotXBlk(pin, ID, res)

    Parameters
    ----------
    pin: connected input port
    ID: CAN node ID
    res: encoder resolution
    kp:  Proportional gain
    ki:  Derivative gain

    Returns
    -------
    blk  : RCPblk
"""
    if(size(pin) != 1):
        raise ValueError("Block should have 1 input port; received %i." % size(pout))

    blk = RCPblk('MCLM_can_motX',pin,[],[0,0],1,[res, kp, kd],[ID, zero])
    return blk

def MCLM_EncBlk(pout, ID, res):
    """Create MCLM_ENC block 

    Get encoder value from an maxon epos driver

    Call: MCLM_EncBlk(pout, ID, res)

    Parameters
    ----------
    pout: connected output port
    ID: CAN node ID
    res: encoder resolution

    Returns
    -------
    blk  : RCPblk
"""
    if(size(pout) != 1):
        raise ValueError("Block should have 1 output port; received %i." % size(pout))

    blk = RCPblk('MCLM_can_enc',[],pout,[0,0],0,[res],[ID])
    return blk

def MCLM_ADBlk(pout, ID):
    """Create MCLM_AD block 

    Get encoder value from an maxon epos driver

    Call: MCLM_DABlk(pout, ID)

    Parameters
    ----------
    pout: connected output port
    ID: CAN node ID

    Returns
    -------
    blk  : RCPblk
"""
    if(size(pout) != 1):
        raise ValueError("Block should have 1 output port; received %i." % size(pout))

    blk = RCPblk('MCLM_can_AD',[],pout,[0,0],0,[],[ID])
    return blk

def MCLM_CO_MotXBlk(pin, ID, res):
    """Create MCLM_MOTX block 

    Get input data from an external file
    
    Call: MCLM_MotXBlk(pin, ID, res)

    Parameters
    ----------
    pin: connected input port
    ID: CAN node ID
    res: encoder resolution

    Returns
    -------
    blk  : RCPblk
"""
    if(size(pin) != 1):
        raise ValueError("Block should have 1 input port; received %i." % size(pout))

    blk = RCPblk('MCLM_canopen_motX',pin,[],[0,0],1,[res],[ID])
    return blk

def MCLM_CO_EncBlk(pout, ID, res):
    """Create MCLM_ENC block 

    Get encoder value from an maxon epos driver

    Call: MCLM_EncBlk(pout, ID, res)

    Parameters
    ----------
    pout: connected output port
    ID: CAN node ID
    res: encoder resolution

    Returns
    -------
    blk  : RCPblk
"""
    if(size(pout) != 1):
        raise ValueError("Block should have 1 output port; received %i." % size(pout))

    blk = RCPblk('MCLM_canopen_enc',[],pout,[0,0],0,[res],[ID])
    return blk

def getXMLindex(file,ref):
    import xml.etree.ElementTree as ET
    from os import system

    system('rm -fr binaries sources resources modelDescription.xml')
    cmd = 'unzip -o ' + file + ".fmu -x 'sources/*' >/dev/null"
    system(cmd)

    ind = -1;
    tree = ET.parse('modelDescription.xml')
    root = tree.getroot()
    cs=root.findall('./ModelVariables/ScalarVariable')
    for el in cs:
        if el.attrib.get('name')==ref:
            ind = int(el.attrib.get('valueReference'))
    
    system('rm -fr binaries/ sources/ resources/ modelDescription.xml')
    return ind

def getXMGUI(file):
    import xml.etree.ElementTree as ET
    from os import system

    system('rm -fr binaries sources resources modelDescription.xml')
    cmd = 'unzip -o ' + file + ".fmu -x 'sources/*' >/dev/null"
    system(cmd)

    tree = ET.parse('modelDescription.xml')
    root = tree.getroot()
    guid = root.attrib.get('guid')
    return guid

def FmuBlk(pin, pout, IN_ref, OUT_ref, Path, dt, ft):
    """Create an interface to a FMU system 

    Call: FmuBlk(pin, pout, ID, IN_ref, OUT_ref, Path)

    Parameters
    ----------
    pin     : connected input ports
    pout    : connected output ports
    IN_ref  : vector with the references to the FMU inputs
    OUT_ref : vector with the references to the FMU outputs
    Path    : Path to the resources folder
    dt      : Major step for integration (must be equal to the sampling time)
    ft      : Feedthrough flah
    
    Returns
    -------
    blk  : RCPblk
"""
    if size(pin) != size(IN_ref):
        raise ValueError("Input references not correct; received %i." % size(IN_ref))

    if size(pout) != size(OUT_ref):
        raise ValueError("Input references not correct; received %i." % size(OUT_ref))
    
    intPar = hstack((size(pin), size(pout)))
    for ref in IN_ref:
        ind = getXMLindex(Path,ref)
        if ind == -1:
            raise ValueError('Reference value not found!')
        else:
            intPar = hstack((intPar, ind))

    for ref in OUT_ref:
        ind = getXMLindex(Path,ref)
        if ind == -1:
            raise ValueError('Reference value not found!')
        else:
            intPar = hstack((intPar, ind))

    guid = getXMGUI(Path)
    strPar =  guid + '|' + Path
    
    blk = RCPblk('FMUinterface',pin,pout,[0,0],ft,[dt],intPar, strPar)
    return blk

def FmuInBlk(pout, OUT_ref, Path, dt):
    """Create an interface to a FMU system 

    Call: FmuInBlk(pout, ID, IN_ref, OUT_ref, Path)

    Parameters
    ----------
    pout    : connected output ports
    OUT_ref : vector with the references to the FMU outputs
    Path    : Path to the resources folder
    dt      : Major step for integration (must be equal to the sampling time)
    
    Returns
    -------
    blk  : RCPblk
"""
    if size(pout) != size(OUT_ref):
        raise ValueError("Input references not correct; received %i." % size(OUT_ref))
    
    intPar = hstack((0, size(pout)))
    for ref in OUT_ref:
        ind = getXMLindex(Path,ref)
        if ind == -1:
            raise ValueError('Reference value not found!')
        else:
            intPar = hstack((intPar, ind))

    guid = getXMGUI(Path)
    strPar =  guid + '|' + Path
    
    blk = RCPblk('FMUinterface',[],pout,[0,0],0,[dt],intPar, strPar)
    return blk

def genericBlk(pin, pout, nx, uy, rP, iP, strP, fname):
    """Create an interface to a generic C function 

    Call: genericBlk()

    Parameters
    ----------
    pin     : connected input ports
    pout    : connected output ports
    nx      : states [cont, disc]
    uy      : Feedforw input->output
    rP      : real parameters
    iP:     : integer parameters
    strP:   : Block string
    fname   : filename (implementation file .c)
    
    Returns
    -------
    blk  : RCPblk
"""
    blk = RCPblk(fname,pin,pout,nx,uy,rP,iP, strP)
    return blk

def epos_MotIBlk(pin, ID, propGain, intGain):
    """Create EPOS_MOTI block 

    Get input data from an external file
    
    Call: epos_MotIBlk(pin, ID, PropGain, IntgGain)

    Parameters
    ----------
    pin: connected input port
    ID: CAN node ID
    PropGain: Proportional gain of the epos torque controller
    IntgGain: Integral gain of the epos torque controller

    Returns
    -------
    blk  : RCPblk
"""
    if(size(pin) != 1):
        raise ValueError("Block should have 1 input port; received %i." % size(pout))

    blk = RCPblk('epos_canopen_motI',pin,[],[0,0],1,[propGain, intGain],[ID])
    return blk

def epos_MotXBlk(pin, ID, propGain, intGain, derGain, Vff, Aff):
    """Create EPOS_MOTI block 

    Get input data from an external file
    
    Call: epos_MotXBlk(pin, ID, propGain, intgGain, derGain, Vff, Aff)

    Parameters
    ----------
    pin: connected input port
    ID: CAN node ID
    propGain: Proportional gain of the epos position controller
    intgGain: Integral gain of the epos position controller
    derGain:  Derivative gain of the epos position controller
    Vff    : Velocity Fedd Forward Factor
    Aff    : Acceleration Feed Forward Factor

    Returns
    -------
    blk  : RCPblk
"""
    if(size(pin) != 1):
        raise ValueError("Block should have 1 input port; received %i." % size(pout))

    blk = RCPblk('epos_canopen_motX',pin,[],[0,0],1,[propGain, intGain, derGain, Vff, Aff],[ID])
    return blk

def epos_EncBlk(pout, ID, res):
    """Create EPOS_ENC block 

    Get encoder value from an maxon epos driver

    Call: epos_EncBlk(pout, ID, res)

    Parameters
    ----------
    pout: connected output port
    ID: CAN node ID
    res: encoder resolution

    Returns
    -------
    blk  : RCPblk
"""
    if(size(pout) != 1):
        raise ValueError("Block should have 1 output port; received %i." % size(pout))

    blk = RCPblk('epos_canopen_enc',[],pout,[0,0],0,[4*res],[ID])
    return blk

def maxon_MotBlk(pin, ID, propGain, intGain):
    """Create MAXON_MOT block 

    Maxon driver for torque control

    Call: maxon_MotBlk(pin, ID)

    Parameters
    ----------
    pin: connected input port
    ID: CAN node ID

    Returns
    -------
    blk  : RCPblk
"""
    if(size(pin) != 1):
        raise ValueError("Block should have 1 input port; received %i." % size(pout))

    blk = RCPblk('maxon_mot',pin,[],[0,0],1,[propGain, intGain],[ID])
    return blk

def maxon_EncBlk(pout, ID, res):
    """Create MAXON_ENC block 

    Maxon driver for encoder

    Call: maxon_EncBlk(pout, ID, res)

    Parameters
    ----------
    pout: connected output port
    ID: CAN node ID
    res: encoder resolution

    Returns
    -------
    blk  : RCPblk
"""
    if(size(pout) != 1):
        raise ValueError("Block should have 1 output port; received %i." % size(pout))

    blk = RCPblk('maxon_enc',[],pout,[0,0],0,[4*res],[ID])
    return blk

def epos_areadBlk(pout, ID, ch):
    """Create EPOS_ANALOG READ block 

    Get analog value from an maxon epos driver

    Call: epos_areadBlk(pout, ID, ch)

    Parameters
    ----------
    pout: connected output port
    ID: CAN node ID
    ch : Analog input channel

    Returns
    -------
    blk  : RCPblk
"""
    if(size(pout) != 1):
        raise ValueError("Block should have 1 output port; received %i." % size(pout))

    blk = RCPblk('epos_canopen_aread',[],pout,[0,0],0,[],[ID, ch])
    return blk

def init_encBlk(pin, pout, trgtime, defv, offset):
    """Create INIT OUTPUT block 

    Initialize the output of a block to a given value

    Call: init_encBlk(pin, pout, trgtime, defv, offset)

    Parameters
    ----------
    pin: connected input port
    pout: connected output port
    trgtime: time to fix the output
    defv : default value up to trigger time
    offset: offset to add to the output

    Returns
    -------
    blk  : RCPblk
"""
    if (size(pout) != 1) or (size(pin) != 1):
        raise ValueError("Block should have 1 input and 1 output port; received %i and %i." % (size(pin),size(pout)))

    blk = RCPblk('init_enc',pin,pout,[0,0],1,[trgtime, defv, offset, 0.0],[])
    return blk

def rtxmlServerBlk(P1, P2, P3, Par, port):
    """Create RTXMLSERVER block 

    Initialize the rtxml http server

    Call: rtxmlserverBlk(P1, P2, P3, Par, port)

    Parameters
    ----------
    P1   : list of Signals for Plot 1
    P2   : list of Signals for Plot 2
    P3   : list of Signals for Plot 3
    Par  : Additional parameters
    port : HTTP port

        Returns
    -------
    blk  : RCPblk
"""
    xmlsettings = '<PLOT1>'
    plt = P1.split()
    for n in range(0,size(plt)):
        xmlsettings += '<SIGNAL' + str(n+1) + '>'+plt[n] + '</SIGNAL' + str(n+1) + '>'
    xmlsettings += '</PLOT1><PLOT2>'
    plt = P2.split()
    for n in range(0,size(plt)):
        xmlsettings += '<SIGNAL' + str(n+1) + '>'+plt[n] + '</SIGNAL' + str(n+1) + '>'
    xmlsettings += '</PLOT2><PLOT3>'
    plt = P3.split()
    for n in range(0,size(plt)):
        xmlsettings += '<SIGNAL' + str(n+1) + '>'+plt[n] + '</SIGNAL' + str(n+1) + '>'
    xmlsettings += '</PLOT3>'
    xmlsettings += Par
        
    blk = RCPblk('rtxmlserver_fnc',[],[],[0,0],0,[],[3140,port],xmlsettings)
    return blk

def rtxmlSigInBlk(pout, Sig, defV):
    """Create XML SIGNAL block 

    Block to send signals to HTTP server

    Call: rtxmlSigInBlk(pin, Sig, DefV)

    Parameters
    ----------
    pin: connected input port
    Sig: Signal name
    DefV: Default Value

    Returns
    -------
    blk  : RCPblk
"""
    if size(pout) != 1:
        raise ValueError("Block should have 1 input port; received %i !" % size(pin))

    blk = RCPblk('rtxmlsignal_fnc',[],pout,[0,0],0,[defV],[0],Sig)
    return blk

def rtxmlSigOutBlk(pin, Sig, defV):
    """Create XML SIGNAL block 

    Block to send signals to HTTP server

    Call: rtxmlSigOutBlk(pin, Sig)

    Parameters
    ----------
    pin: connected input port
    Sig: Signal name
    DefV: Default Value

    Returns
    -------
    blk  : RCPblk
"""
    if size(pin) != 1:
        raise ValueError("Block should have 1 input port; received %i !" % size(pin))

    blk = RCPblk('rtxmlsignal_fnc',pin,[],[0,0],1,[defV],[1],Sig)
    return blk

def comediADBlk(pout, dev, ch, cr):
    """Create Comedi Analog to Digital block
    Call: comediADBlk(pout,dev,ch,range,ref)

    Parameters
    ----------
    pout   -  output pin 
    dev    -  Comedi device
    ch     -  Channel
    cr     -  analog range
    
    Returns
    -------
    blk  : RCPblk
"""
    if size(pout) != 1:
        raise ValueError("Block should have 1 input port; received %i !" % size(pout))

    blk = RCPblk('comedi_analog_input',[],pout,[0,0],0,[],[ch, cr],dev)
    return blk

def comediDABlk(pin, dev, ch, cr):
    """Create Comedi Digital to Analog block
    Call: comediDABlk(pin, dev,ch,range,ref)

    Parameters
    ----------
    pin    -  input pin
    dev    -  Comedi device
    ch     -  Channel
    cr     -  analog range
    
    Returns
    -------
    blk  : RCPblk
"""
    if size(pin) != 1:
        raise ValueError("Block should have 1 input port; received %i !" % size(pin))

    blk = RCPblk('comedi_analog_output',pin,[],[0,0],1,[],[ch, cr],dev)
    return blk

def comediDIBlk(pout, dev, ch):
    """Create Comedi Digital Input block
    Call: comediDIBlk(pout, dev,ch)

    Parameters
    ----------
    pout   -  output pin 
    dev    -  Comedi device
    ch     -  Channel
    
    Returns
    -------
    blk  : RCPblk
"""
    if size(pout) != 1:
        raise ValueError("Block should have 1 input port; received %i !" % size(pout))

    blk = RCPblk('comedi_digital_input',[],pout,[0,0],0,[],[ch],dev)
    return blk

def comediDOBlk(pin, dev, ch, thr):
    """Create Comedi Digital Output block
    Call: comediDOBlk(pin,dev,ch)

    Parameters
    ----------
    pin    -  Input pin
    dev    -  Comedi device
    ch     -  Channel
    
    Returns
    -------
    blk  : RCPblk
"""
    if size(pin) != 1:
        raise ValueError("Block should have 1 input port; received %i !" % size(pin))

    blk = RCPblk('comedi_digital_output',pin,[],[0,0],1,[thr],[ch],dev)
    return blk

def switchBlk(pin,pout, cond, val, pers):
    """Create switch block 

    Call: switchBlk(pin, pout, cond, val, pers)

    Parameters
    ----------
    pin: connected input ports (3)
    pout: connected output port
    cond:  0 >, 1 <
    val:   value to compare
    pers:  switch can change again (0) or is fixed (1)

    Output switches from input 1 to input 2 if the condition is reached
    (input 3 > or <) than val;
    If pers is 1 the system doesn't switch back again if the condition is
    no more satisfied
    
    Returns
    -------
    blk  : RCPblk
"""
    if(size(pin) != 3):
        raise ValueError("Block should have 3 input ports; received %i." % size(pin))

    if(size(pout) != 1):
        raise ValueError("Block should have 1 output port; received %i." % size(pout))

    blk = RCPblk('switcher',pin,pout,[0,0],1,[val],[cond, pers])
    return blk

def lutBlk(pin, pout, coeff):
    """Create a Look Up Table block with polynomial curve 

    Call: lutBlk(pin, pout, coeff)

    Parameters
    ----------
    pin: connected input ports (3)
    pout: connected output port
    coeff:  polynomial coefficients
    
    Returns
    -------
    blk  : RCPblk
"""
    if(size(pin) != 1):
        raise ValueError("Block should 1 input port; received %i." % size(pin))

    if(size(pout) != 1):
        raise ValueError("Block should have 1 output port; received %i." % size(pout))

    blk = RCPblk('lut',pin,pout,[0,0],1,[coeff],[size(coeff)])
    return blk

def intgBlk(pin,pout,X0=0.0):
    """Create integral block 

    Continous integral block

    Call: intgBlk(pin,pout,X0)

    Parameters
    ----------
    pin : connected input port
    pout: connected output port
    X0: Initial conditions

    Returns
    -------
    blk  : RCPblk
"""
    nin = size(pin)
    if (nin != 1):
        raise ValueError("Block have 1 input: received %i input ports" % nin)
    
    nout = size(pout)
    if(nout != 1):
        raise ValueError("Block have 1 output1: received %i output ports" % nout)
        
    blk = RCPblk('integral',pin,pout,[1,0],0,[0.0 ,X0],[])
    return blk


def zdelayBlk(pin,pout,X0=0.0):
    """Create unit delay block 

    Continous integral block

    Call: zdelayBlk(pin,pout,X0)

    Parameters
    ----------
    pin : connected input port
    pout: connected output port
    X0: Initial conditions

    Returns
    -------
    blk  : RCPblk
"""
    nin = size(pin)
    if (nin != 1):
        raise ValueError("Block have 1 input: received %i input ports" % nin)
    
    nout = size(pout)
    if(nout != 1):
        raise ValueError("Block have 1 output1: received %i output ports" % nout)
        
    blk = RCPblk('unitDelay',pin,pout,[0,1],0,[X0],[])
    return blk

def trigBlk(pin,pout,tp):
    """Create trigonometric block 

    Trigonometric block

    Call: intgBlk(pin,pout,type sin=1 cos=2 tan=3)

    Parameters
    ----------
    pin : connected input port
    pout: connected output port
    type: Math function

    Returns
    -------
    blk  : RCPblk
"""
    nin = size(pin)
    if (nin != 1):
        raise ValueError("Block have 1 input: received %i input ports" % nin)
    
    nout = size(pout)
    if(nout != 1):
        raise ValueError("Block have 1 output1: received %i output ports" % nout)
        
    blk = RCPblk('trigo',pin,pout,[0,0],1,[],[tp])
    return blk

def unixsocketCBlk(pin,sockname):
    """Create Unix Socket block 

    Unix Socket block - Client

    Call: unixsocketBlk(pin,socketname)

    Parameters
    ----------
    pin : connected input port
    type: Socket name (string)

    Returns
    -------
    blk  : RCPblk
"""
    blk = RCPblk('unixsockC',pin,[],[0,0],1,[],[0],'/tmp/'+sockname)
    return blk

def unixsocketSBlk(pout,sockname,defvals):
    """Create Unix Socket block - Server 

    Unix Socket block

    Call: unixsocketBlk(pin,socketname)

    Parameters
    ----------
    pin      : connected input port
    type     : Socket name (string)
    defvals  : Default outputs

    Returns
    -------
    blk  : RCPblk
"""
    outputs = len(pout)
    vals = zeros(outputs,float)
    if len(defvals) > outputs:
        N=outputs
    else:
        N = len(defvals)

    for n in range(N):
        vals[n]=defvals[n]
        
    blk = RCPblk('unixsockS',[],pout,[0,0],0,defvals,[0,0],'/tmp/'+sockname)
    return blk

def MCLM_MotXBlk(pin, ID, res, kp, kd, zero):
    """Create MCLM_MOTX block 

    Get input data from an external file
    
    Call: MCLM_MotXBlk(pin, ID, res)

    Parameters
    ----------
    pin: connected input port
    ID: CAN node ID
    res: encoder resolution
    kp:  Proportional gain
    ki:  Derivative gain

    Returns
    -------
    blk  : RCPblk
"""
    if(size(pin) != 1):
        raise ValueError("Block should have 1 input port; received %i." % size(pout))

    blk = RCPblk('MCLM_can_motX',pin,[],[0,0],1,[res, kp, kd],[ID, zero])
    return blk

def MCLM_EncBlk(pout, ID, res):
    """Create MCLM_ENC block 

    Get encoder value from an maxon epos driver

    Call: MCLM_EncBlk(pout, ID, res)

    Parameters
    ----------
    pout: connected output port
    ID: CAN node ID
    res: encoder resolution

    Returns
    -------
    blk  : RCPblk
"""
    if(size(pout) != 1):
        raise ValueError("Block should have 1 output port; received %i." % size(pout))

    blk = RCPblk('MCLM_can_enc',[],pout,[0,0],0,[res],[ID])
    return blk

def MCLM_ADBlk(pout, ID):
    """Create MCLM_AD block 

    Get encoder value from an maxon epos driver

    Call: MCLM_DABlk(pout, ID)

    Parameters
    ----------
    pout: connected output port
    ID: CAN node ID

    Returns
    -------
    blk  : RCPblk
"""
    if(size(pout) != 1):
        raise ValueError("Block should have 1 output port; received %i." % size(pout))

    blk = RCPblk('MCLM_can_AD',[],pout,[0,0],0,[],[ID])
    return blk

def MCLM_CO_MotXBlk(pin, ID, res):
    """Create MCLM_MOTX block 

    Get input data from an external file
    
    Call: MCLM_MotXBlk(pin, ID, res)

    Parameters
    ----------
    pin: connected input port
    ID: CAN node ID
    res: encoder resolution

    Returns
    -------
    blk  : RCPblk
"""
    if(size(pin) != 1):
        raise ValueError("Block should have 1 input port; received %i." % size(pout))

    blk = RCPblk('MCLM_canopen_motX',pin,[],[0,0],1,[res],[ID])
    return blk

def MCLM_CO_EncBlk(pout, ID, res):
    """Create MCLM_ENC block 

    Get encoder value from an maxon epos driver

    Call: MCLM_EncBlk(pout, ID, res)

    Parameters
    ----------
    pout: connected output port
    ID: CAN node ID
    res: encoder resolution

    Returns
    -------
    blk  : RCPblk
"""
    if(size(pout) != 1):
        raise ValueError("Block should have 1 output port; received %i." % size(pout))

    blk = RCPblk('MCLM_canopen_enc',[],pout,[0,0],0,[res],[ID])
    return blk

def getXMLindex(file,ref):
    import xml.etree.ElementTree as ET
    from os import system

    system('rm -fr binaries sources resources modelDescription.xml')
    cmd = 'unzip -o ' + file + ".fmu -x 'sources/*' >/dev/null"
    system(cmd)

    ind = -1;
    tree = ET.parse('modelDescription.xml')
    root = tree.getroot()
    cs=root.findall('./ModelVariables/ScalarVariable')
    for el in cs:
        if el.attrib.get('name')==ref:
            ind = int(el.attrib.get('valueReference'))
    
    system('rm -fr binaries/ sources/ resources/ modelDescription.xml')
    return ind

def getXMGUI(file):
    import xml.etree.ElementTree as ET
    from os import system

    system('rm -fr binaries sources resources modelDescription.xml')
    cmd = 'unzip -o ' + file + ".fmu -x 'sources/*' >/dev/null"
    system(cmd)

    tree = ET.parse('modelDescription.xml')
    root = tree.getroot()
    guid = root.attrib.get('guid')
    return guid

def FmuBlk(pin, pout, IN_ref, OUT_ref, Path, dt, ft):
    """Create an interface to a FMU system 

    Call: FmuBlk(pin, pout, ID, IN_ref, OUT_ref, Path)

    Parameters
    ----------
    pin     : connected input ports
    pout    : connected output ports
    IN_ref  : vector with the references to the FMU inputs
    OUT_ref : vector with the references to the FMU outputs
    Path    : Path to the resources folder
    dt      : Major step for integration (must be equal to the sampling time)
    ft      : Feedthrough flah
    
    Returns
    -------
    blk  : RCPblk
"""
    if size(pin) != size(IN_ref):
        raise ValueError("Input references not correct; received %i." % size(IN_ref))

    if size(pout) != size(OUT_ref):
        raise ValueError("Input references not correct; received %i." % size(OUT_ref))
    
    intPar = hstack((size(pin), size(pout)))
    for ref in IN_ref:
        ind = getXMLindex(Path,ref)
        if ind == -1:
            raise ValueError('Reference value not found!')
        else:
            intPar = hstack((intPar, ind))

    for ref in OUT_ref:
        ind = getXMLindex(Path,ref)
        if ind == -1:
            raise ValueError('Reference value not found!')
        else:
            intPar = hstack((intPar, ind))

    guid = getXMGUI(Path)
    strPar =  guid + '|' + Path
    
    blk = RCPblk('FMUinterface',pin,pout,[0,0],ft,[dt],intPar, strPar)
    return blk

def FmuInBlk(pout, OUT_ref, Path, dt):
    """Create an interface to a FMU system 

    Call: FmuInBlk(pout, ID, IN_ref, OUT_ref, Path)

    Parameters
    ----------
    pout    : connected output ports
    OUT_ref : vector with the references to the FMU outputs
    Path    : Path to the resources folder
    dt      : Major step for integration (must be equal to the sampling time)
    
    Returns
    -------
    blk  : RCPblk
"""
    if size(pout) != size(OUT_ref):
        raise ValueError("Input references not correct; received %i." % size(OUT_ref))
    
    intPar = hstack((0, size(pout)))
    for ref in OUT_ref:
        ind = getXMLindex(Path,ref)
        if ind == -1:
            raise ValueError('Reference value not found!')
        else:
            intPar = hstack((intPar, ind))

    guid = getXMGUI(Path)
    strPar =  guid + '|' + Path
    
    blk = RCPblk('FMUinterface',[],pout,[0,0],0,[dt],intPar, strPar)
    return blk

def genericBlk(pin, pout, nx, uy, rP, iP, strP, fname):
    """Create an interface to a generic C function 

    Call: genericBlk()

    Parameters
    ----------
    pin     : connected input ports
    pout    : connected output ports
    nx      : states [cont, disc]
    uy      : Feedforw input->output
    rP      : real parameters
    iP:     : integer parameters
    strP:   : Block string
    fname   : filename (implementation file .c)
    
    Returns
    -------
    blk  : RCPblk
"""
    blk = RCPblk(fname,pin,pout,nx,uy,rP,iP, strP)
    return blk

def init_maxon_MotBlk(ID, propGain, intGain):
    """Initialize MAXON_MOT block 

    Get input data from an external file
    
    Call: epos_MotIBlk(pin, ID, PropGain, IntgGain)

    Parameters
    ----------
    ID: CAN node ID
    PropGain: Proportional gain of the epos torque controller
    IntgGain: Integral gain of the epos torque controller

    Returns
    -------
    blk  : RCPblk
"""
    blk = RCPblk('init_maxon_Mot',[],[],[0,0],0,[propGain, intGain],[ID])
    return blk

def init_epos_MotIBlk(ID, propGain, intGain):
    """Initialize EPOS_MOT_I block 

    Get input data from an external file
    
    Call: epos_MotIBlk(pin, ID, PropGain, IntgGain)

    Parameters
    ----------
    ID: CAN node ID
    PropGain: Proportional gain of the epos torque controller
    IntgGain: Integral gain of the epos torque controller

    Returns
    -------
    blk  : RCPblk
"""
    blk = RCPblk('init_epos_MotI',[],[],[0,0],0,[propGain, intGain],[ID])
    return blk

def can_sdo_sendBlk(pin, ID, index, subindex, data, useInp):
    """send a standard CAN message
    
    Call: can_SDO_sendBlk(pin, ID, index, subindex, data, useInp)

    Parameters
    ----------
    ID: CAN node ID
    index : message index
    subindex: message subindex
    data: message data
    useInp: input go to next block

    Returns
    -------
    blk  : RCPblk
"""
    blk = RCPblk('can_sdo_send',pin,[],[0,0],1,[],[ID, index, subindex, data, useInp])
    return blk

def can_sdo_sendThBlk(pin, pout, ID, index, subindex, data, useInp):
    """send a standard CAN message
    
    Call: can_SDO_sendBlk(pin, ID, index, subindex, data, useInp)

    Parameters
    ----------
    ID: CAN node ID
    index : message index
    subindex: message subindex
    data: message data
    useInp: input go to next block

    Returns
    -------
    blk  : RCPblk
"""
    blk = RCPblk('can_sdo_send',pin,pout,[0,0],1,[],[ID, index, subindex, data, useInp])
    return blk

def can_sdo_recvBlk(pout, ID, index, subindex, K):
    """receive a standard CAN message
    
    Call: can_SDO_recvBlk(pout, ID, index, subindex, K)

    Parameters
    ----------
    ID: CAN node ID
    index : message index
    subindex: message subindex
    K: Multiplicative factor to output value

    Returns
    -------
    blk  : RCPblk
"""
    retID = 0x580+ID
    blk = RCPblk('can_sdo_recv',[],pout,[0,0],0,[K],[ID, index, subindex, retID])
    return blk

def can_gen_recvBlk(pout, ID, retID, index, subindex, K):
    """receive a standard CAN message
    
    Call: can_SDO_recvBlk(pout, ID, index, subindex, K)

    Parameters
    ----------
    ID: CAN node ID
    index : message index
    subindex: message subindex
    K: Multiplicative factor to output value

    Returns
    -------
    blk  : RCPblk
"""
    blk = RCPblk('can_gen_recv',[],pout,[0,0],0,[K],[ID, index, subindex, retID])
    return blk
