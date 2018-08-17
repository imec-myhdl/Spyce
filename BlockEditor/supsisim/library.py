#!/usr/bin/python
# aim for python 2/3 compatibility
from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

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
from supsisim.dialg import txtDialog,LibraryChoice_Dialog

from lxml import etree

import libraries

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
        
        self.viewMenu = QtWidgets.QMenu("Views")
        
        self.menuBlk.addMenu(self.viewMenu)
        
        
    def addViewMenu(self):
        views = libraries.getViews(self.actComp.blockname,self.actComp.libname)
        for key in views.keys():
            if key != 'diagram' and key != 'icon':
                def getFunction(key):
                    def viewAction():
                        self.parent.openView(key,self.actComp)
                    return viewAction
                viewAction = getFunction(key)
                action = self.viewMenu.addAction(key+" view")
                action.triggered.connect(viewAction)
        
    def contextMenuEvent(self, event):
        pos = event.scenePos()
        for item in self.items(QtCore.QRectF(pos-QtCore.QPointF(DB,DB), QtCore.QSizeF(2*DB,2*DB))):
            if isinstance(item, Block):
                self.viewMenu.clear()
                self.addViewMenu()
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
            c = self.actComp
            attributes = {'name':c.name,'input':c.inp,'output':c.outp,'icon':c.icon,'flip':c.flip,'libname':c.libname,'type':c.type}
            data = '@'.join([str(attributes),str(c.parameters),str(c.properties),c.blockname,c.libname])
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
        if pinlist:
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
        #blockname = block.name
        svgiconname = os.path.join(respath, 'blocks', block.icon+'.svg')
        #svgfilename = os.path.join(respath, 'blocks', blockname+'.svg')
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
                shutil.move(svgtempfilename, svgiconname)
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
            for libname in libraries.libs:
                bb = []
                for blockname in libraries.libs[libname]:
                    print(blockname,libname)
                    block = libraries.getBlock(blockname,libname)
                    bb.append(block.toPython(lib=True))
                t.append('libs[{}] = [ \\\n    {}]'.format(repr(libname), ', \n    '.join(bb)))
            
            print('\n'.join(t)+'\n')
                        
        except OSError:
            raise Exception('Inkscape is not installed')
        
        return dwg


        
class Library(QtWidgets.QMainWindow):
    '''
    '''
    def __init__(self,parent=None):
        super(Library, self).__init__(parent)

#        self.centralWidget = QtWidgets.QWidget()
        self.resize(800, 500)
        self.setWindowTitle('Library')
        self.libConfig = ()
#        self.readLib()
        self.addToolbars()
        self.closeFlag = False
        
        dialog = LibraryChoice_Dialog(self)
        ret = dialog.exec_()
        if ret == 0:
            self.listView()
#            mypath = respath + '/icons/'
#            textViewAction = QtWidgets.QAction(QtGui.QIcon(mypath+'textIcon.png'),
#                                                    '&text view', self,
#                                                    triggered = self.textView)             
#            
#            self.toolbar.addAction(textViewAction)
        else:
            self.symbolView()
    
    def addToolbars(self):
        mypath = respath + '/icons/'
        self.listViewAction = QtWidgets.QAction(QtGui.QIcon(mypath+'listView.png'),
                                                '&List View', self,
                                                triggered = self.listView)
        
        self.symbolViewAction = QtWidgets.QAction(QtGui.QIcon(mypath+'symbolView.png'),
                                                '&Symbol View', self,
                                                triggered = self.symbolView)        
        
        self.toolbar = self.addToolBar('File')
        self.toolbar.addAction(self.listViewAction)
        self.toolbar.addAction(self.symbolViewAction)  
    
    
    def switchToListView(self):
        mypath = respath + '/icons/'
        textViewAction = QtWidgets.QAction(QtGui.QIcon(mypath+'textIcon.png'),
                                                '&text view', self,
                                                triggered = self.textView)             
        
        self.toolbar.addAction(textViewAction)    
        self.listView()
    
    def openView(self,type,actComp=None):
        import supsisim.const
        reload(supsisim.const)
        from supsisim.const import viewEditors           
        
        if self.type == 'symbolView':
            blockname = actComp.blockname
            libname = actComp.libname
        else:
            libname = self.libraries.currentItem().text()
            blockname = self.cells.currentItem().text()
        
        source = libraries.getViews(blockname,libname)[type]
        editor = viewEditors[type]
        os.system(editor + " " + source)
    
        #reset library
        if self.type == 'symbolView':
            i = self.tabs.currentIndex()
            self.symbolView()
            self.tabs.setCurrentIndex(i)
        else:
            l = self.libraries.currentRow()
            c = self.cells.currentRow()
            self.listView()
            self.libraries.setCurrentRow(l)
            self.cells.setCurrentRow(c)
    def textView(self):
        if self.libraries.currentItem() and self.cells.currentItem():
            self.openView('text')
    
    def listView(self):
        self.type = 'listView'
        reload(libraries)
        self.centralWidget = QtWidgets.QWidget()        
        
        self.libraries = QtWidgets.QListWidget(self.centralWidget)
        #self.catogories = QtWidgets.QListWidget(self.centralWidget)
        self.cells = QtWidgets.QListWidget(self.centralWidget)
        self.views = QtWidgets.QListWidget(self.centralWidget)
        
        self.libraries.currentItemChanged.connect(self.clickLibrary)
        #self.catogories.currentItemChanged.connect(self.clickCatogory)
        self.cells.currentItemChanged.connect(self.clickCell)
        self.views.currentItemChanged.connect(self.clickView)
        
        
        
        self.libs = libraries.libs
        libnames = self.libs.keys()
        self.libraries.addItems(libnames)
         
        
        self.layout = QtWidgets.QHBoxLayout(self.centralWidget)
        
        self.layout.addWidget(self.libraries)
        #self.layout.addWidget(self.catogories)
        self.layout.addWidget(self.cells)
        self.layout.addWidget(self.views)
        
        self.setCentralWidget(self.centralWidget)
        
        self.cells.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.cells.customContextMenuRequested.connect(self.onContext)
        
        
        
    def onContext(self,point):
        menu = QtWidgets.QMenu()
        libname = self.libraries.currentItem().text()
        blockname = self.cells.currentItem().text()
        views = libraries.getViews(blockname,libname)
        for key in views.keys():
            if key != 'diagram' and key != 'icon':
                def getFunction(key):
                    def viewAction():
                        self.openView(key)
                    return viewAction
                viewAction = getFunction(key)
                action = menu.addAction(key+" view")
                action.triggered.connect(viewAction)
        menu.exec_(self.cells.mapToGlobal(point))

    def symbolView(self):
        self.type = 'symbolView'
        reload(libraries)
        self.centralWidget = QtWidgets.QWidget()
#        self.resize(800, 500)
#        self.setWindowTitle('Library')
#        self.libConfig = ()
##        self.readLib()
#        self.closeFlag = False

        self.tabs = QtWidgets.QTabWidget()
        self.quickSelTab = QtWidgets.QComboBox()
        
        libs = libraries.libs
        libnames = sorted(libs.keys(), key=lambda s: s.lower())
        self.quickSelTab.addItems(libnames)
        for libname in libnames: # case insensitive sorting
            
            lib = libs[libname]
            diagram = CompViewer(self)
            view = QtWidgets.QGraphicsView(diagram)
            diagram.compLock = True
            for i, blockname in enumerate(lib):
                cell = libraries.getBlock(blockname,libname)
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
            if libname == 'symbols':
                self.symbolTab = tab
            layout = QtWidgets.QVBoxLayout()
            layout.addWidget(view)
            tab.setLayout(layout)

            self.tabs.addTab(tab, libname)
            self.quickSelTab.currentIndexChanged.connect(self.setCurrentTab)
            
                
        layout = QtWidgets.QHBoxLayout()
        self.tabs.setCornerWidget(self.quickSelTab, QtCore.Qt.TopLeftCorner)
        layout.addWidget(self.tabs)
        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(layout)
        self.setCentralWidget(self.widget)
        ix = self.quickSelTab.findText(libraries.default)
        self.tabs.setCurrentIndex(ix)
        self.quickSelTab.setCurrentIndex (ix)
        
    def clickLibrary(self):
        library = self.libraries.currentItem()
        if(library):
            self.cells.clear()
            for cell in self.libs[library.text()]:
                self.cells.addItem(cell)
        
    def clickCatogory(self):
        catogory = self.catogories.currentItem().text()
        
    def clickCell(self):
        cell = self.cells.currentItem()
        if(cell):
            mimeData = QtCore.QMimeData()
            data = '@'.join([self.libraries.currentItem().text(), cell.text()])
            mimeData.setText(data)
            drag = QtGui.QDrag(self)
            drag.setMimeData(mimeData)
            drag.exec_(QtCore.Qt.CopyAction)
        
    def clickView(self):
        view = self.views.currentItem().text()



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
