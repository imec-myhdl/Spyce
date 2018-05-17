#!/usr/bin/python
# aim for python 2/3 compatibility
from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

import Qt
from  Qt import QtGui, QtWidgets, QtCore # see https://github.com/mottosso/Qt.py

import sys
#if sys.version_info>(3,0):
#    import sip
#    sip.setapi('QString', 1)

import tempfile
import subprocess
import shutil

import svgwrite
                   
from supsisim.const import DB, PD, respath, svgpinlabels

#import dircache
import os

from supsisim.block import Block
from supsisim.dialg import txtDialog

from lxml import etree

import imeclib

class CompViewer(QtWidgets.QGraphicsScene):
    def __init__(self, parent=None):
        super(CompViewer, self).__init__()
        self.parent = parent
        self.actComp = None

        self.componentList = []	 
        self.activeComponent = None 

        self.menuBlk = QtWidgets.QMenu()
        
        # create context menu
        editIconAction   = self.menuBlk.addAction('edit Icon')
        editIconAction.triggered.connect(self.editIcon)

        createIconAction = self.menuBlk.addAction('(re)create Icon')
        createIconAction.triggered.connect(self.createIcon)

        editPinsAction   = self.menuBlk.addAction('Edit pins')
        editPinsAction.triggered.connect(self.editPins)
 
    def contextMenuEvent(self, event):
        pos = event.scenePos()
        for item in self.items(QtCore.QRectF(pos-QtCore.QPointF(DB,DB), QtCore.QSizeF(2*DB,2*DB))):
            if isinstance(item, Block):
                self.menuBlk.exec_(event.screenPos())
                break
        else:
            print('Hmmm, here is nothing?!?')

    def setUniqueName(self, block):
        return block.name


    def mousePressEvent(self, event):
        x = event.scenePos().x()
        y = event.scenePos().y()

        t = QtGui.QTransform()
        self.actComp = self.itemAt(x, y, t)
        

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton and isinstance(self.actComp, Block):
            mimeData = QtCore.QMimeData()
            if self.actComp.iosetble:
                io = '1'
            else:
                io = '0'
            c = self.actComp
            data = '@'.join([c.name, str(c.inp), str(c.outp), io, c.icon, c.params])
            mimeData.setText(data)
            drag = QtGui.QDrag(self.parent)
            drag.setMimeData(mimeData)
            drag.exec_(QtCore.Qt.CopyAction)
            
            

    def mouseReleaseEvent(self, event):
        pass

        
    def editPins(self):
        block = self.actComp
        inputs, outputs, inouts = block.pins()
        d = txtDialog('Pins of {}'.format(block.name))
        pinlist = d.editList(inputs + outputs + inouts, header='io x y name')
        
        for p in block.ports():
            p.setParentItem(None) # effectively removing port
            
        block.inp  = []
        block.outp = []
        for tp, x, y, name in pinlist:
            if tp == 'i':
                block.add_inPort([name, x, y])
                block.inp.append([name, x, y])
            elif tp == 'o':
                block.add_outPort([name, x, y])
                block.outp.append([name, x, y])
            else:
                print('{} is not an implemented io type'.format(tp))
        block.update()

    def editIcon(self):
        '''edit svg file'''
        block = self.actComp
        blockname = block.name
        svgiconname = os.path.join(respath, 'blocks', block.icon+'.svg')
        svgfilename = os.path.join(respath, 'blocks', blockname+'.svg')
        with open(svgiconname) as fi:
            t = fi.read()
        #generate a tempfile
        fo = tempfile.NamedTemporaryFile(suffix='.svg', delete=False)
        svgtempfilename = fo.name
        fo.write(t)
        fo.close()

        try:
            timestamp0 = os.stat(svgtempfilename).st_mtime
            subprocess.call('inkscape {}'.format(svgtempfilename).split())
            timestamp1 = os.stat(svgtempfilename).st_mtime
            if  timestamp0 < timestamp1: # newer => copy'
                shutil.move(svgtempfilename, svgfilename)
                block.setIcon()
                
            # creanup tempfile
            if os.path.exists(svgtempfilename):
                os.remove(svgtempfilename)
                
        except OSError:
            raise Exception('Inkscape is not installed')
        
        
        

    def createIcon(self):
        '''generate svg file'''
        block = self.actComp
        blockname = block.name
        inputs, outputs, inouts = block.pins()
        pinlist = inputs + outputs + inouts
        
        # find bounding box
        x0, y0, x1, y1 = None, None, None, None
        for tp, x, y, pname in pinlist:
            x0 = x if x0 == None else min(x0, x)
            x1 = x if x1 == None else max(x1, x)
            y0 = y if y0 == None else min(y0, y)
            y1 = y if y1 == None else max(y1, y)
        
        w = x1-x0 + PD
        h = max(50, y1 - y0 + PD) # block height
        dh2 = (h - (y1 - y0))/2
        y0 = y0 - dh2
        y1 = y1 + dh2
        
        
        # defaults to be moved to conf
        margin    = 10
        font_size = 10 # height
        pin_size  = 10 # length of line segment 
        
        #generate a tempfile
        f = tempfile.NamedTemporaryFile(suffix='.svg', delete=False)
        svgtempfilename = f.name
        f.close()
                
        dwg = svgwrite.Drawing(filename=svgtempfilename, size=(2*margin+x1-x0,2*margin+y1-y0), profile='tiny', debug=False)
        dwg.attribs['xmlns:sodipodi'] = "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"  
        dwg.attribs['xmlns:inkscape'] = "http://www.inkscape.org/namespaces/inkscape"
        dwg.attribs['id'] = "svg2"
        dwg.attribs['inkscape:version'] = "0.91 r13725"
        dwg.attribs['sodipodi:docname'] = blockname
        
        sodipodi = svgwrite.base.BaseElement(debug=False)
        sodipodi.elementname = 'sodipodi:namedview'
        t = '''objecttolerance="10"
               gridtolerance="10000"
               guidetolerance="10"
               showgrid="true"
               inkscape:snap-grids="true"
               inkscape:current-layer="svg2"
               inkscape:window-width="{w}"
               inkscape:window-height="{h}"'''.format(w=w, h=h)
        g =  svgwrite.base.BaseElement(type="xygrid", units="px", spacingx="10", spacingy="10", debug=False)
        g.elementname = 'inkscape:grid'
        sodipodi.elements.append(g)
        
        for line in t.splitlines():
            k, v = line.split('=')
            sodipodi.attribs[k.strip()] = v.strip().strip('"')
        dwg.elements.append(sodipodi)
        
        for tp, x, y, name in pinlist:
            extra = dict()
            extra['font-size'] = '{}px'.format(font_size)
            x -= x0 - margin
            y -= y0 - margin
            if tp == 'i': # left align
                dx, dy = pin_size, 0
                tx, ty = x + dx + font_size*0.35, y + font_size*0.35
            elif tp == 'o': # right align
                extra['text-anchor'] = "end"
                dx, dy = -pin_size, 0
                tx, ty = x + dx - font_size*0.35, y + dy + font_size*0.35
            elif tp == 'io': # mid align
                extra['text-anchor'] = "mid"
                dx, dy = 0, -pin_size
                tx, ty = dx, dy

            if svgpinlabels:
                dwg.add(dwg.text(name, id='{}-portlabel_{}'.format(tp, name), insert=(tx, ty), **extra))
            dwg.add(dwg.line(id='{}-port_{}'.format(tp, name), start=(x, y), end=(x+dx, y+dy), stroke='darkGreen'))
        
        
        dwg.add(dwg.rect(insert=(margin+pin_size, margin+pin_size), size=(x1-x0-2*pin_size, y1-y0-2*pin_size),
                            fill='none', stroke='darkGreen', stroke_width=1))
        
        dwg.save(pretty=True)
        
        try:
            timestamp0 = os.stat(svgtempfilename).st_mtime
            subprocess.call('inkscape {}'.format(svgtempfilename).split())
            timestamp1 = os.stat(svgtempfilename).st_mtime
            svgfilename = os.path.join(respath, 'blocks', blockname+'.svg')
            if not os.path.exists(svgfilename):# not existing => copy'
                shutil.move(svgtempfilename, svgfilename)
                block.setIcon()
                
            elif  timestamp0 < timestamp1:# newer => copy'
                shutil.move(svgtempfilename, svgfilename)
                block.setIcon()
            else: # ask
                msg = "Not modified: Do you want to store the auto-generated icon??"
                reply =QtWidgets. QMessageBox.question(None, 'Message', 
                                 msg, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)

                if reply == QtWidgets.QMessageBox.Yes:
                     shutil.move(svgtempfilename, svgfilename)
                     block.setIcon()

            if os.path.exists(svgtempfilename):
                os.remove(svgtempfilename)
                
                
            
            t = ['# -*- coding: utf-8 -*-']
            t.append('# auto-saved file')
            t.append('# edits outside blocks will be lost')
            t.append('')
            t.append('from supsisim.block import Block')
            t.append('from collections import OrderedDict')
            t.append('')
            t.append('libs = OrderedDict()')
            for c in imeclib.libs:
                bb = []
                for block in imeclib.libs[c]:
                    bb.append(block.toPython(lib=True))
                t.append('libs[{}] = [ \\\n    {}]'.format(repr(c), ', \n    '.join(bb)))
            
            print('\n'.join(t)+'\n')
                        
        except OSError:
            raise Exception('Inkscape is not installed')
        
        return dwg


        
class Library(QtWidgets.QMainWindow):
    '''
    '''

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

        self.centralWidget = QtWidgets.QWidget()
        self.resize(800, 500)
        self.setWindowTitle('Library')
        self.libConfig = ()
#        self.readLib()
        self.closeFlag = False

        self.tabs = QtWidgets.QTabWidget()
        self.quickSelTab = QtWidgets.QComboBox()
        
        libs = imeclib.libs
        libnames = sorted(libs.keys(), key=lambda s: s.lower())
        self.quickSelTab.addItems(libnames)
        for libname in libnames: # case insensitive sorting
            
            lib = libs[libname]
            diagram = CompViewer(self)
            view = QtWidgets.QGraphicsView(diagram)
            diagram.compLock = True
            for i, cell in enumerate(lib):
                px = i % 2
                py = i/2
                diagram.addItem(cell)
                cell.scene = diagram
                cell.setPos(px*150,py*150)
                cell.setup()
                w = cell.boundingRect().width()
                h = cell.boundingRect().height()
                if h > 100.0:
                    set_orient(cell, scale=min(1.0, 80.0/w, 100.0/h))
            tab = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout()
            layout.addWidget(view)
            tab.setLayout(layout)

            self.tabs.addTab(tab, libname)
            self.quickSelTab.currentIndexChanged.connect(self.setCurrentTab)
#            self.connect(self.quickSelTab, QtCore.SIGNAL('currentIndexChanged (int)'), self.setCurrentTab)
            
                
        layout = QtWidgets.QHBoxLayout()
        self.tabs.setCornerWidget(self.quickSelTab, QtCore.Qt.TopLeftCorner)
        layout.addWidget(self.tabs)
        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(layout)
        self.setCentralWidget(self.widget)
        ix = self.quickSelTab.findText(imeclib.default)
        self.tabs.setCurrentIndex(ix)
        self.quickSelTab.setCurrentIndex (ix)


    def wheelEvent(self, event):
        if Qt.__binding__ in ['PyQt5', 'PySide2']:
            factor = 1.41 ** (-event.angleDelta().y()/ 240.0)
        else:
            factor = 1.41 ** (-event.delta() / 240.0)
        
        # zoom around mouse position, not the anchor
        self.setTransformationAnchor(QtWidgets.QGraphicsView.NoAnchor)
        self.setResizeAnchor(QtWidgets.QGraphicsView.NoAnchor)
        pos = self.mapToScene(event.pos())
        self.scale(factor, factor)
        delta =  self.mapToScene(event.pos()) - pos
        self.translate(delta.x(), delta.y())


    def setCurrentTab(self, ix):
        self.tabs.setCurrentIndex(ix)
#        self.quickSelTab.setEditText(str(ix))
        
    def readLib(self):
        files = os.listdir(os.path.join(respath,'blocks'))
        for f in sorted(files):
            if f.endswith('.blk'):
                tree = etree.parse(os.path.join(respath, 'blocks', f))
                root = tree.getroot()
                line = root.findtext('library/name')
                b = (line, )
                blocks = root.findall('library/blockdata')
                for iter in blocks:
                    name = iter.findtext('blockname')
                    ip = int(iter.findtext('inputs'))
                    op = int(iter.findtext('outputs'))
                    st = int(iter.findtext('settable'))
                    icon = iter.findtext('icon')
                    params = iter.findtext('params')
                    bb = (name,)+(ip,)+(op,)+(st,)+(icon,)+(params,)
                    b = b +(bb,)

                self.libConfig = self.libConfig + (b,)
        
    def closeEvent(self,event):
        if self.closeFlag:
            event.accept()
        else:
            event.ignore()


    def mouseRightButtonPressed(self, obj, event):
        item = self.itemAt(event.scenePos())
        if isinstance(item, Block):
            self.menuBlk.exec_(event.screenPos())
        else:
            pass

def set_orient(item, flip=False, scale=0, rotate=0, combine=False):
    '''returns QTransform, operation order: flip (mirror in Y axis), scale, rorate (in degrees)'''
    if flip:
        item.setTransform(QtGui.QTransform.fromScale(-scale, scale).rotate(rotate), combine)
    else:
         item.setTransform(QtGui.QTransform.fromScale(scale, scale).rotate(rotate), combine)




if __name__ == '__main__':
    import logging
    logging.basicConfig()
    app = QtWidgets.QApplication(sys.argv)

    library = Library()
    library.setGeometry(20, 20, 400, 500)
    library.show()

    app.exec_()
    sys.exit()
