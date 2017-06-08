"""
This is a procedural interface to the RCPblk library

roberto.bucher@supsi.ch

The following class is provided:

  RCPblk      - class with info for Rapid Controller Prototyping

The following commands are provided:

  genCode        - Create  C code from BlockDiagram
  genMake        - Generate the Makefile for the C code
  detBlkSeq      - Get the right block sequence for simulation and RT
  sch2blks       - Generate block list fron schematic
  
"""
from scipy import mat, size, array, zeros
from numpy import  nonzero, ones
from os import environ
import sys
from supsisim.RCPblk import RCPblk

class RCPblk:
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
        str += "Outputs ports      : " + self.pout.__str__() + "\n"
        str += "Nr. of states      : " + self.nx.__str__() + "\n"
        str += "Relation u->y      : " + self.uy.__str__() + "\n"
        str += "Real parameters    : " + self.realPar.__str__() + "\n"
        str += "Integer parameters : " + self.intPar.__str__() + "\n"
        str += "String Parameter   : " + self.str.__str__() + "\n"
        return str

def genCode(model, Tsamp, blocks, rkstep = 10):
    """Generate C-Code

    Call: genCode(model, Tsamp, Blocks, rkstep)

    Parameters
    ----------
    model     : Model name
    Tsamp     : Sampling Time
    Blocks    : Block list
    rkstep    : step division pro sample time for fixed step solver

    Returns
    -------
    -
"""
    maxNode = 0
    for blk in blocks:
        for n in range(0,size(blk.pin)):
            if blk.pin[n] > maxNode:
                maxNode = blk.pin[n]
        for n in range(0,size(blk.pout)):
            if blk.pout[n] > maxNode:
                maxNode = blk.pout[n]

    # Check outputs not connected together!
    outnodes = zeros(maxNode+1)
    for blk in blocks:
        for n in range(0,size(blk.pout)):
            if outnodes[blk.pout[n]] == 0:
                outnodes[blk.pout[n]] = 1
            else:
                raise ValueError('Problem in diagram: outputs connected together!')           
    
    Blocks = detBlkSeq(maxNode, blocks)
    if size(Blocks) == 0:
        raise ValueError('No possible to determine the block sequence')
    
    fn = model + '.c'
    f=open(fn,'w')
    strLn = "#include <pyblock.h>\n#include <stdio.h>\n\n"
    f.write(strLn)
    N = size(Blocks)

    totContBlk = 0
    for blk in Blocks:
        totContBlk += blk.nx[0]

    f.write("/* Function prototypes */\n\n")

    for blk in Blocks:
        strLn = "void " + blk.fcn + "(int Flag, python_block *block);\n"
        f.write(strLn)

    f.write("\n")

    strLn = "double " + model + "_get_tsamp()\n"
    strLn += "{\n"
    strLn += "  return (" + str(Tsamp) + ");\n"
    strLn += "}\n\n"
    f.write(strLn)

    strLn = "python_block block_" + model + "[" + str(N) + "];\n\n"
    f.write(strLn);

    for n in range(0,N):
        blk = Blocks[n]
        if (size(blk.realPar) != 0):
            strLn = "static double realPar_" + str(n) +"[] = {"
            strLn += str(mat(blk.realPar).tolist())[2:-2] + "};\n"
            f.write(strLn)
        if (size(blk.intPar) != 0):
            strLn = "static int intPar_" + str(n) +"[] = {"
            strLn += str(mat(blk.intPar).tolist())[2:-2] + "};\n"
            f.write(strLn)
        strLn = "static int nx_" + str(n) +"[] = {"
        strLn += str(mat(blk.nx).tolist())[2:-2] + "};\n"
        f.write(strLn)
    f.write("\n")

    f.write("/* Nodes */\n")
    for n in range(1,maxNode+1):
        strLn = "static double Node_" + str(n) + "[] = {0.0};\n"
        f.write(strLn)

    f.write("\n")

    f.write("/* Input and outputs */\n")
    for n in range(0,N):
        blk = Blocks[n]
        nin = size(blk.pin)
        nout = size(blk.pout)
        if (nin!=0):
            strLn = "static void *inptr_" + str(n) + "[]  = {"
            for m in range(0,nin):
                strLn += "0,"
            strLn = strLn[0:-1] + "};\n"
            f.write(strLn)
        if (nout!=0):
            strLn = "static void *outptr_" + str(n) + "[] = {"
            for m in range(0,nout):
                strLn += "0,"
            strLn = strLn[0:-1] + "};\n"
            f.write(strLn)

    f.write("\n\n")

    f.write("/* Initialization function */\n\n")
    strLn = "int " + model + "_init()\n"
    strLn += "{\n"
    f.write(strLn)
    for n in range(0,N):
        blk = Blocks[n]
        nin = size(blk.pin)
        nout = size(blk.pout)

        if (nin!=0):
            for m in range(0,nin):
                strLn = "  inptr_" + str(n) + "[" + str(m) + "]  = (void *) Node_" + str(blk.pin[m]) + ";\n"
                f.write(strLn)
        if (nout!=0):
            for m in range(0,nout):
                strLn = "  outptr_" + str(n) + "[" + str(m) + "] = (void *) Node_" + str(blk.pout[m]) + ";\n"
                f.write(strLn)
    f.write("\n")

    f.write("/* Block definition */\n\n")
    for n in range(0,N):
        blk = Blocks[n]
        nin = size(blk.pin)
        nout = size(blk.pout)

        strLn =  "  block_" + model + "[" + str(n) + "].nin  = " + str(nin) + ";\n"
        strLn += "  block_" + model + "[" + str(n) + "].nout = " + str(nout) + ";\n"

        port = "nx_" + str(n)
        strLn += "  block_" + model + "[" + str(n) + "].nx   = " + port + ";\n"

        if (nin == 0):
            port = "NULL"
        else:
            port = "inptr_" + str(n)
        strLn += "  block_" + model + "[" + str(n) + "].u    = " + port + ";\n"
        if (nout == 0):
            port = "NULL"
        else:
            port = "outptr_" + str(n)
        strLn += "  block_" + model + "[" + str(n) + "].y    = " + port + ";\n"
        if (size(blk.realPar) != 0):
            par = "realPar_" + str(n)
        else:
            par = "NULL"
        strLn += "  block_" + model + "[" + str(n) + "].realPar = " + par + ";\n"
        if (size(blk.intPar) != 0):
            par = "intPar_" + str(n)
        else:
            par = "NULL"
        strLn += "  block_" + model + "[" + str(n) + "].intPar = " + par + ";\n"
        strLn += "  block_" + model + "[" + str(n) + "].str = " +'"' + blk.str + '"' + ";\n"
        strLn += "  block_" + model + "[" + str(n) + "].ptrPar = NULL;\n"
        f.write(strLn)
        f.write("\n")
    f.write("\n")

    f.write("/* Set initial outputs */\n\n")

    for n in range(0,N):
        blk = Blocks[n]
        strLn = "  " + blk.fcn + "(INIT, &block_" + model + "[" + str(n) + "]);\n"
        f.write(strLn)
    f.write("\n")

    for n in range(0,N):
        blk = Blocks[n]
        strLn = "  " + blk.fcn + "(OUT, &block_" + model + "[" + str(n) + "]);\n"
#        f.write(strLn)
    f.write("\n")

    for n in range(0,N):
        blk = Blocks[n]
        if (blk.nx[1] != 0):
            strLn = "  " + blk.fcn + "(STUPD, &block_" + model + "[" + str(n) + "]);\n"
            f.write(strLn)
    f.write("}\n\n")

    f.write("/* ISR function */\n\n")
    strLn = "int " + model + "_isr(double t)\n"
    strLn += "{\n"
    f.write(strLn)

    if (totContBlk != 0):
        f.write("int i, j;\n")
        f.write("double h;\n\n")

    for n in range(0,N):
        blk = Blocks[n]
        strLn = "  " + blk.fcn + "(OUT, &block_" + model + "[" + str(n) + "]);\n"
        f.write(strLn)
    f.write("\n")

    for n in range(0,N):
        blk = Blocks[n]
        if (blk.nx[1] != 0):
            strLn = "  " + blk.fcn + "(STUPD, &block_" + model + "[" + str(n) + "]);\n"
            f.write(strLn)
    f.write("\n")

    if (totContBlk != 0):
        strLn = "  h = " + model + "_get_tsamp()/" + str(rkstep) + ";\n\n"
        f.write(strLn)

        for n in range(0,N):
            blk = Blocks[n]
            if (blk.nx[0] != 0):
                strLn = "  block_" + model + "[" + str(n) + "].realPar[0] = h;\n"
                f.write(strLn)
            
        strLn = "  for(i=0;i<" + str(rkstep) + ";i++){\n"
        f.write(strLn)
        for n in range(0,N):
            blk = Blocks[n]
            if (blk.nx[0] != 0):
                strLn = "    " + blk.fcn + "(OUT, &block_" + model + "[" + str(n) + "]);\n"
                f.write(strLn)

        for n in range(0,N):
            blk = Blocks[n]
            if (blk.nx[0] != 0):
                strLn = "    " + blk.fcn + "(STUPD, &block_" + model + "[" + str(n) + "]);\n"
                f.write(strLn)

        f.write("  }\n")

    f.write("}\n")

    f.write("/* Termination function */\n\n")
    strLn = "int " + model + "_end()\n"
    strLn += "{\n"
    f.write(strLn)
    for n in range(0,N):
        blk = Blocks[n]
        strLn = "  " + blk.fcn + "(END, &block_" + model + "[" + str(n) + "]);\n"
        f.write(strLn)
    f.write("}\n\n")
    f.close()

def genMake(model, template, addObj = ''):
    """Generate the Makefile

    Call: genMake(model, template)

    Parameters
    ----------
    model     : Model name
    template  : Template makefile
    addObj    : Additional object files

    Returns
    -------
    -
"""
    template_path = environ.get('PYSUPSICTRL')
    fname = template_path + '/CodeGen/templates/' + template
    f = open(fname,'r')
    mf = f.read()
    f.close()
    mf = mf.replace('$$MODEL$$',model)
    mf = mf.replace('$$ADD_FILES$$',addObj)
    f = open('Makefile','w')
    f.write(mf)
    f.close()

def new_detBlkSeq(Nodes, blocks):
    """Generate the Block sequence for simulation and RT

    Call: detBlkSeq(Nodes, Blocks)

    Parameters
    ----------
    Nodes     : Number of total nodes in diagram
    blocks    : List with the unordered blocks

    Returns
    -------
    Blocks    : List with the ordered blocks
    
"""
    class nodeClass:
        def __init__(self, N):
            self.PN = N
            self.connected_in = None
            self.connected_out = []
            self.updated = False

        def __str__(self):
            txt  = 'Node: ' + self.PN.__str__() + '\n'
            try:
                txt += 'Block In: ' + self.connected_in.fcn + '\n'
            except:
                txt += 'No Block\n'

            txt += ' Blocks out:\n'
            for item in self.connected_out:
                try:
                    txt += item.fcn + '\n'
                except:
                    txt += 'None\n'
            txt += self.updated.__str__() + '\n'
            return txt

    def fillNodeList(nN,blks):
        nL = []
        nL.append(nodeClass(0))
        for n in range(1, nN+1):
            node = nodeClass(n)
            nL.append(node)
        for blk in blks:
            for n in blk.pin:
                nL[n].connected_out.append(blk)
            for n in blk.pout:
                nL[n].connected_in = blk
        return nL

    def checkBlock(blk, nL, bk_in, bk_out):
        if blk in bk_in:
            if blk.uy == 1:
                upd = True
                for n in blk.pin:
                    upd = upd and nL[n].updated
            if blk.uy == 0 or upd:
                bk_out.append(blk)
                bk_in.remove(blk)
                for n in blk.pout:
                    nd = nL[n]
                    nd.updated = True
                if len(blk.pout) != 0:
                    nn = blk.pout[0]
                    node = nL[nn]
                    for item in node.connected_out:
                        checkBlock(item, nL, bk_in, bk_out)

    nodeList = fillNodeList(Nodes, blocks)
        
    blks_in = list(blocks)
    blks_out = []

    nrec = sys.getrecursionlimit()
    nb = len(blks_in)
    if nb > 100:
        sys.setrecursionlimit(10*nb)
    nBout = -1
    while len(blks_out) != nBout:
        nBout = len(blks_out)
#        for blk in blks_in:
#            checkBlock(blk, nodeList, blks_in, blks_out)
        for item in nodeList:
            checkBlock(item.connected_in, nodeList, blks_in, blks_out)
            

    if len(blks_in) != 0:
        for blk in blks_in:
            print(blk)
        raise ValueError("Algeabric loop!")

    sys.setrecursionlimit(nrec)
    
    return blks_out

def detBlkSeq(Nodes, blocks):
    """Generate the Block sequence for simulation and RT

    Call: detBlkSeq(Nodes, Blocks)

    Parameters
    ----------
    Nodes     : Number of total nodes in diagram
    blocks    : List with the unordered blocks

    Returns
    -------
    Blocks    : List with the ordered blocks
    
"""
    M = size(blocks);
    seq = []
    dep = zeros((M,M))

    # Fill the dependency table
    for n in range(0,Nodes):
        node = n+1
        for m in range(0,M):
            blk1 = blocks[m]
            linked1 = size(nonzero(blk1.pin==node))
            if (linked1 != 0) and (blk1.uy == 1):
                for k in range(0,M):
                    blk2 = blocks[k]
                    linked2 = size(nonzero(blk2.pout==node))
                    if linked2 != 0:
                        dep[m,k] = 1
    blks = []
    m = 0
    n = M
    placed_blocks = ones((1,M))
    while (m != M) and (n != 0):
        for k in range(0,M):
            if placed_blocks[0,k] == 1:
                cnt = size(nonzero(dep[k,:] == 1))
                if cnt == 0:
                    blks.append(blocks[k])

                    dep[:,k] = 0
                    placed_blocks[0,k] = 0
        m = m+1
        n = size(nonzero(placed_blocks == 1))
    
    if n != 0:
        print(placed_blocks)
        raise ValueError("Algeabric loop!")
    
    return blks
   
