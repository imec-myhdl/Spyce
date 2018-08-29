#!/usr/bin/python
# aim for python 2/3 compatibility
from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

import sys
import Qt
from  Qt import QtGui, QtWidgets, QtCore # see https://github.com/mottosso/Qt.py


from supsisim.block import Block, textItem
from supsisim.port import Port, InPort, OutPort
from supsisim.node import Node
from supsisim.connection import Connection
from supsisim.dialg import RTgenDlg
from supsisim.const import pyrun, TEMP
from lxml import etree
import os
import subprocess
import time

import libraries

class GraphicsView(QtWidgets.QGraphicsView):
    def __init__(self, parent=None,symbol=False):
        super(GraphicsView, self).__init__(parent)
        self.symbol = symbol
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.setSceneRect(QtCore.QRectF(-2000, -2000, 4000, 4000))
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setRenderHint(QtGui.QPainter.TextAntialiasing)
        self.setAcceptDrops(True)
        self.returnSymbol = False
        
    def wheelEvent(self, event):
        if Qt.__binding__ in ['PyQt5', 'PySide2']:
            factor = 1.41 ** (-event.angleDelta().y()/ 240.0)
        else:
            factor = 1.41 ** (-event.delta() / 240.0)
        
        # zoom around mouse position, not the anchor
        self.setTransformationAnchor(QtWidgets.QGraphicsView.NoAnchor)
        self.setResizeAnchor(QtWidgets.QGraphicsView.NoAnchor)
        pos = self.mapToScene(event.pos())
        self.scale(1/factor, 1/factor)
        delta =  self.mapToScene(event.pos()) - pos
        self.translate(delta.x(), delta.y())
        
class Scene(QtWidgets.QGraphicsScene):
    def __init__(self, main, parent=None):
        super(Scene,self).__init__(parent)
        self.mainw = main
        self.nameList = []
        self.selection = []

        self.template = 'sim.tmf'
        self.addObjs = ''
        self.Ts = '0.01'
        self.script = ''
        self.Tf = '10'      
        self.selectionChanged.connect(self.selectionChangedSlot) 


    def getIndex(self,name):
        try:
            index = self.nameList.index(name)
        except:
            index = -1
        return index

    def setUniqueName(self, block):
        cnt = 1
        nm = block.name
        while self.getIndex(nm) != -1:
            nm = nm.rstrip('0123456789') + str(cnt)
            cnt += 1
        self.nameList.append(nm)
        self.nameList.sort()
        return nm
    
    def selectionChangedSlot(self):
        for item in self.items():
            if isinstance(item, Node):
                if not item in self.selectedItems():
                    item.setFlag(item.ItemIsMovable,False)
    
    def dragEnterEvent(self, event):
        event.accept()

    def dragMoveEvent(self, event):
        event.accept()
          
    def dragLeaveEvent(self, event):
        event.accept()
        
    def dropEvent(self, event):
        if event.mimeData().text() == 'Node':
            n = Node(None,self)
            n.setPos(event.scenePos())
        elif event.mimeData().text() == 'Comment':
            comment = textItem('', anchor=3, parent=None,comment=True)
            comment.setDefaultTextColor(QtGui.QColor('darkGray'))
            comment.setPos(event.scenePos())
            self.addItem(comment)
            comment.setFocus()
        else:
            if self.mainw.library.type == "symbolView":
                data = event.mimeData().text().split('@')
                if self.mainw.view.symbol and self.mainw.centralWidget.libname == data[0] and self.mainw.centralWidget.blockname == data[1]:
                    pass
                else:
                    
                    b = libraries.getBlock(data[1],data[0],scene=self)                    
                    b.setPos(event.scenePos())
#                    b = Block(eval(data[0]),eval(data[1]),eval(data[2]),data[3],data[4],None, self)
            else:
                data = event.mimeData().text().split('@')
                if self.mainw.view.symbol and self.mainw.centralWidget.libname != data[0] and self.mainw.centralWidget.blockname == data[1]:
                    pass
                else:
                    libs = libraries.libs
                    for blockname in libs[data[0]]:
                        if(blockname == data[1]):
                            b = libraries.getBlock(blockname,data[0],scene=self)                    
                            b.setPos(event.scenePos())

    def newDgm(self):
        items = self.items()
        for item in items:
            for thing in item.childItems():
                if isinstance(thing, Port):
                    for conn in thing.connections:
                        conn.remove()
            self.removeItem(item)
        self.addObjs=''
        self.script=''
        self.Tf='10.0'
        self.nameList = []
    
    def savePython(self,fname):
        blocks = []
        connections = []
        nodes = []        
    
        for item in self.items():
            if isinstance(item,Block):
                blocks.append(str(item.toPython()))
            if isinstance(item,Connection):
                connections.append(str(item.toPython()))
            if isinstance(item,Node):
                nodes.append(str(item.toPython()))
        
        f = open(fname,'w+')
        f.write("blocks = [" + ",\n          ".join(blocks) + "]\n\n" + 
                    "connections = [" + ",\n               ".join(connections) + "]\n\n" + 
                    "nodes = [" + ",\n         ".join(nodes) + "]")
        f.close()
    
    def loadPython(self,fname,path,center=True):
        sys.path.append(path)
        exec('import ' + fname)
        reload(eval(fname))
        
        blocks = eval(fname + '.blocks')
        connections = eval(fname + '.connections')
        nodes = eval(fname + '.nodes')
        
        for block in blocks:
            if 'parameters' in block.keys():
                b = libraries.getBlock(block['blockname'],block['libname'],scene=self,param=block['parameters'],name=block['name'])
            else:
                b = libraries.getBlock(block['blockname'],block['libname'],scene=self,name=block['name'])
            b.setPos(block['pos']['x'],block['pos']['y'])
            b.properties = block['properties']
        for node in nodes:
            n = Node(None,self)
            n.setPos(node['pos']['x'],node['pos']['y'])
            if 'label' in node:
                n.label = textItem(node['label'], anchor=3, parent=n)
                n.label.setPos(0,20)
        for connection in connections:        
            conn = Connection(None,self)
            conn.pos1 = QtCore.QPointF(connection['pos1']['x'],connection['pos1']['y'])
            conn.pos2 = QtCore.QPointF(connection['pos2']['x'],connection['pos2']['y'])
            conn.update_ports_from_pos()
            if 'label' in connection:
                conn.label = textItem(connection['label'], anchor=3, parent=conn)
                conn.label.setPos(conn.pos2.x(),conn.pos2.y())
            if 'signalType' in connection:
                conn.signalType = textItem(connection['signalType'], anchor=3, parent=conn)
                conn.signalType.setPos(conn.pos2.x(),conn.pos2.y())
        if center:
            self.mainw.view.centerOn(self.getCenter()[0],self.getCenter()[1])
    
    def getCenter(self):
        coordinatesX = []
        coordinatesY = []
        for item in self.items():
            if isinstance(item, Block) or isinstance(item,Node):
                coordinatesX.append(item.x())
                coordinatesY.append(item.y())
        if len(coordinatesX):
            return sum(coordinatesX)/len(coordinatesX),sum(coordinatesY)/len(coordinatesY)
        else:
            point = self.mainw.view.mapToScene(self.mainw.view.viewport().width()/2,self.mainw.view.viewport().height()/2)        
            return point.x(),point.y()
    
    
    def saveDgm(self,fname):
        items = self.items()
        dgmBlocks = []
        dgmNodes = []
        dgmConnections = []
        for item in items:
            if isinstance(item, Block):
                dgmBlocks.append(item)
            elif isinstance(item, Node):
                dgmNodes.append(item)
            elif isinstance(item, Connection):
                dgmConnections.append(item)
            else:
                pass

        root = etree.Element('root')
        now = etree.SubElement(root,'Date')
        etree.SubElement(now, 'SavingDate').text = time.strftime("%d.%m.%Y - %H:%M:%S")
        sim = etree.SubElement(root,'Simulation')
        etree.SubElement(sim,'Template').text = self.template
        etree.SubElement(sim,'Ts').text = self.Ts
        etree.SubElement(sim,'AddObj').text = self.addObjs
        etree.SubElement(sim,'ParScript').text = self.script
        etree.SubElement(sim,'Tf').text = self.Tf
        for item in dgmBlocks:
            item.save(root)
        for item in dgmNodes:
            item.save(root)
        for item in dgmConnections:
            item.save(root)
        f = open(fname,'w')
        msg = etree.tostring(root, pretty_print=True)
        msg = msg.decode()
        f.write(msg)
        f.close()

    def loadDgm(self, fname):
        tree = etree.parse(fname)
        root = tree.getroot()
        sim = root.findall('Simulation')[0]
        self.template = sim.findtext('Template')
        self.Ts = sim.findtext('Ts')
        self.addObjs = sim.findtext('AddObj')
        if self.addObjs==None or self.addObjs=='':
            self.addObjs=''
        self.script = sim.findtext('ParScript')
        if self.script==None or self.script=='':
            self.script=''
        self.Tf = sim.findtext('Tf')
        if self.Tf==None:
            self.Tf=''

        blocks = root.findall('block')
        for item in blocks:
            self.loadBlock(item)
        nodes = root.findall('node')
        for item in nodes:
            self.loadNode(item)
        connections = root.findall('connection')
        for item in connections:
            self.loadConn(item)
       
    def loadBlock(self, item):
        b = Block(None, self, item.findtext('name'),
                      int(item.findtext('inp')), int(item.findtext('outp')),
                      item.findtext('ioset')=='1', item.findtext('icon'),
                      item.findtext('params'), item.findtext('flip')=='1' )
        b.setPos(float(item.findtext('posX')), float(item.findtext('posY')))

    def loadNode(self, item):
        n = Node(None, self)
        n.setPos(float(item.findtext('posX')), float(item.findtext('posY')))       

    def find_itemAt(self, pos):
        items = self.items(QtCore.QRectF(pos-QtCore.QPointF(1,1), QtCore.QSizeF(3,3)))
        for item in items:
            if isinstance(item, QtWidgets.QGraphicsItem) and not isinstance(item, Connection) and not isinstance(item, textItem):
                return item
        return None
    
    def loadConn(self, item):
        c = Connection(None, self)
        pt1 = QtCore.QPointF(float(item.findtext('pos1X')), float(item.findtext('pos1Y')))
        pt2 = QtCore.QPointF(float(item.findtext('pos2X')), float(item.findtext('pos2Y')))
        c.pos1 = pt1
        c.pos2 = pt2
        c.update_ports_from_pos()
        
    def setParamsBlk(self):
        self.mainw.paramsBlock()

    def codegenDlg(self):
        dialog = RTgenDlg(self)
        dialog.template.setText(self.template)
        dialog.addObjs.setText(self.addObjs)
        dialog.Ts.setText(self.Ts)
        dialog.parscript.setText(self.script)
        dialog.Tf.setText(self.Tf)
        res = dialog.exec_()
        if res != 1:
            return

        self.template = str(dialog.template.text())
        self.addObjs = str(dialog.addObjs.text())
        self.Ts = str(dialog.Ts.text())
        self.script = str(dialog.parscript.text())
        self.Tf = str(dialog.Tf.text())
        
    def codegen(self, flag):
        items = self.items()
        dgmBlocks = []
        for item in items:
            if isinstance(item, Block):
                dgmBlocks.append(item)
            else:
                pass
        
        nid = 1
        for item in dgmBlocks:
            for thing in item.childItems():
                if isinstance(thing, OutPort):
                    thing.nodeID = str(nid)
                    nid += 1
        for item in dgmBlocks:
            for thing in item.childItems():
                if isinstance(thing, InPort):
                    c = thing.connections[0]
                    while not isinstance(c.port1, OutPort):
                        try:
                            c = c.port1.parent.port_in.connections[0]
                        except (AttributeError, ValueError):
                            raise ValueError('Problem in diagram: outputs connected together!')
                    thing.nodeID = c.port1.nodeID
        self.generateCCode()
        try:
            os.mkdir('./' + self.mainw.filename + '_gen')
        except:
            pass
        if flag:
            if self.mainw.runflag:
                cmd = pyrun + ' tmp.py'
                try:
                    p = subprocess.Popen(cmd, shell=True)
                except:
                    pass
                p.wait()
            else:
                print('Generate code -> run -i tmp.py')
        
    def blkInstance(self, item):
        ln = item.parameters.split('|')
        txt = item.name.replace(' ','_') + ' = ' + ln[0] + '('
        if item.inp != 0:
            inp = '['
            for thing in item.childItems():
                if isinstance(thing, InPort):
                    inp += thing.nodeID +','
            inp = inp.rstrip(',') + ']'
            txt += inp + ','
            
        if item.outp != 0:
            outp = '['
            for thing in item.childItems():
                if isinstance(thing, OutPort):
                    outp += thing.nodeID +','
            outp = outp.rstrip(',') + ']'
            txt += outp +','
        txt = txt.rstrip(',')
        N = len(ln)
        for n in range(1,N):
            par = ln[n].split(':')
            txt += ', ' + par[1].__str__()

        txt += ')'
        return txt
    
    def generateCCode(self):
        txt = ''
        if self.mainw.runflag:
            try:
                f = open(self.script,'r')
                txt = f.read()
                f.close()
                txt += '\n'
            except:
                pass
        
        items = self.items()
        txt += 'from supsisim.RCPblk import *\n'
        txt += 'try:\n'
        txt += '    from supsisim.dsPICblk import *\n'
        txt += 'except:\n'
        txt += '    pass\n'        
        txt += 'from supsisim.RCPgen import *\n'
        txt += 'from control import *\n'
        txt += 'import os\n'
        blkList = []
        for item in items:
            if isinstance(item, Block):
                blkList.append(item.name.replace(' ','_'))
                txt += self.blkInstance(item) + '\n'
        fname = self.mainw.filename
        fn = open('tmp.py','w')
        fn.write(txt)
        fn.write('\n')
        txt = 'blks = ['
        for item in blkList:
            txt += item + ','
        txt += ']\n'
        fn.write(txt)
        fnm = './' + fname + '_gen'
                
        fn.write('fname = ' + "'" + fname + "'\n")
        fn.write('os.chdir("'+ fnm +'")\n')
        fn.write('genCode(fname, ' + self.Ts + ', blks)\n')
        fn.write("genMake(fname, '" + self.template + "', addObj = '" + self.addObjs + "')\n")
        fn.write('\nimport os\n')
        fn.write('os.system("make")\n')
        fn.write('os.chdir("..")\n')
        fn.close()

    def simrun(self):
        self.codegen(False)
        cmd  = '\n'
        cmd += 'import matplotlib.pyplot as plt\n'
        cmd += 'import numpy as np\n\n'
        cmd += 'os.system("./' + self.mainw.filename + ' -f ' + self.Tf + '>x.x")\n'
        cmd += 'x = np.loadtxt("x.x")\n'
        cmd += 'N = shape(x)[1]\n'
        cmd += 'if len(x) != 0:\n'
        cmd += '    plt.plot(x[:,0],x[:,1:N])\n'
        cmd += '    plt.grid(), plt.show()\n'
        cmd += 'try:\n'
        cmd += '    os.remove("x.x")\n'
        cmd += 'except:\n'
        cmd += '    pass\n'
        
        try:
            os.mkdir(TEMP + '/' + self.mainw.filename + '_gen')
        except:
            pass
        f = open('tmp.py','a')
        f.write(cmd)
        f.close()
        if self.mainw.runflag:
            cmd = pyrun + ' tmp.py'
            try:
                subprocess.Popen(cmd, shell=True)
            except:
                pass
        else:
            print('Simulate system -> run -i tmp.py')
         
    def debugInfo(self):
        items = self.items()
        dgmBlocks = []
        dgmNodes = []
        dgmConnections = []
        for item in items:
            if isinstance(item, Block):
                dgmBlocks.append(item)
            elif isinstance(item, Node):
                dgmNodes.append(item)
            elif isinstance(item, Connection):
                dgmConnections.append(item)
            else:
                pass
        print('Blocks:')
        for item in dgmBlocks:
            print(item)
        print('\nNodes:')
        for item in dgmNodes:
            print(item)
        print('\nConnections:')
        for item in dgmConnections:
            print(item)
       
