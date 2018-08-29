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
from supsisim.dialg import txtDialog,LibraryChoice_Dialog, textLineDialog, createBlockDialog, error

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
        self.menuLibrary = QtWidgets.QMenu()
        
        # create context menu
        editIconAction   = self.menuBlk.addAction('edit Icon')
        editIconAction.triggered.connect(self.editIcon)

        createIconAction = self.menuLibrary.addAction('Create block')
        createIconAction.triggered.connect(self.parent.createBlock)

        editPinsAction   = self.menuBlk.addAction('Edit pins')
        editPinsAction.triggered.connect(self.editPins)
        
        
        cutBlockAction   = self.menuBlk.addAction('Cut')
        cutBlockAction.triggered.connect(self.cutBlock)
        
        changeIconAction = self.menuBlk.addAction('Change icon')
        changeIconAction.triggered.connect(self.changeIcon)
        
        
        removeBlockAction = self.menuBlk.addAction('Remove block')
        removeBlockAction.triggered.connect(self.removeBlock)
        
        
        self.pasteBlockAction   = self.menuLibrary.addAction('Paste')
        self.pasteBlockAction.triggered.connect(self.parent.pasteBlock)
        
        self.viewMenu = QtWidgets.QMenu("Views")
        
        self.menuBlk.addMenu(self.viewMenu)
    
    def removeBlock(self):
        self.parent.removeBlock(self.actComp)
    
    def changeIcon(self):
        self.parent.changeIcon(self.actComp)
#        filename = QtWidgets.QFileDialog.getOpenFileName(self.parent, 'Open',respath + '/blocks/', filter='*.svg')
#        print(filename)
#        if filename[0]:
#            icon = QtCore.QFileInfo(filename[0]).baseName()
#            path = os.getcwd()
#            fname = '/libraries/library_{}/{}.py'.format(self.actComp.libname,self.actComp.blockname)
#            f = open(path + fname,'r')
#            lines = f.readlines()
#            f.close()
#            
#            for index,line in enumerate(lines):
#                if line.startswith('iconSource = '):
#                    lines[index] = "iconSource = '{}'\n".format(icon)
#            
#            
#            f = open(path + fname,'w+')
#            f.write("".join(lines))
#            f.close()  
#            
#            i = self.parent.tabs.currentIndex()
#            self.parent.symbolView()
#            self.parent.tabs.setCurrentIndex(i)
        
        
    def cutBlock(self):
        self.parent.cutBlock(self.actComp)
#        self.parent.copiedBlock = self.actComp.blockname
#        self.parent.copiedBlockLibname = self.actComp.libname
        
#    def pasteBlock(self):
#        if self.parent.copiedBlock and self.parent.copiedBlockLibname:
#            path = os.getcwd()
#            libname = self.parent.tabs.tabText(self.parent.tabs.currentIndex())
#            if libname != self.parent.copiedBlockLibname:
#                filenames = []
#                views = libraries.getViews(self.parent.copiedBlock,self.parent.copiedBlockLibname)
#                for key in views.keys():
#                    if key != 'icon':
#                        filenames.append(views[key])
#                for filename in filenames:
#                    newFilename = filename.replace('libraries/library_' + self.parent.copiedBlockLibname,'libraries/library_' + libname)
#                    os.rename(path + '/' + filename,path + '/' + newFilename)
#                    try:
#                        os.remove(path + '/' + filename + 'c')
#                    except:
#                        pass
#                    
#                    
#                #change sources
#                    
#                path = os.getcwd()
#                fname = '/libraries/library_{}/{}.py'.format(libname,self.parent.copiedBlock)
#                f = open(path + fname,'r')
#                lines = f.readlines()
#                f.close()
#                
#                for index,line in enumerate(lines):
#                    lines[index] = line.replace('libraries/library_' + self.parent.copiedBlockLibname,'libraries/library_' + libname)
#                    
#                
#                
#                f = open(path + fname,'w+')
#                f.write("".join(lines))
#                f.close()    
#                    
#                
#                i = self.parent.tabs.currentIndex()
#                self.parent.symbolView()
#                self.parent.tabs.setCurrentIndex(i)
     
    
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
            if self.parent.copiedBlock and self.parent.copiedBlockLibname:
                self.pasteBlockAction.setEnabled(True)
            else:
                self.pasteBlockAction.setEnabled(False)
            self.menuLibrary.exec_(event.screenPos())

    def setUniqueName(self, block):
        return block.name


    def mousePressEvent(self, event):
#        x = event.scenePos().x()
#        y = event.scenePos().y()
#       
#
#        t = QtGui.QTransform()
#        self.actComp = self.itemAt(x, y, t)

 
        pos = event.scenePos()
        for item in self.items(QtCore.QRectF(pos-QtCore.QPointF(DB,DB), QtCore.QSizeF(2*DB,2*DB))):
            if isinstance(item, Block):
                self.actComp = item
     

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton and isinstance(self.actComp, Block):
            mimeData = QtCore.QMimeData()
            c = self.actComp
            attributes = {'name':c.name,'input':c.inp,'output':c.outp,'icon':c.icon,'flip':c.flip,'libname':c.libname,'type':c.type}
#            data = '@'.join([str(attributes),str(c.parameters),str(c.properties),c.blockname,c.libname])
            data = '@'.join([c.libname,c.blockname])
            mimeData.setText(data)
            drag = QtGui.QDrag(self.parent)
            drag.setMimeData(mimeData)
            drag.exec_(QtCore.Qt.CopyAction)
            
            

    def mouseReleaseEvent(self, event):
        pass

#    def createBlock(self):
#        libname = self.parent.tabs.tabText(self.parent.tabs.currentIndex())
#        
#        dialog = createBlockDialog()
#        
#        ret = dialog.getRet()
#        
#        if ret:
#            name = ret['name']
#            inp = ret['input']
#            outp = ret['output']
#            icon = ret['icon']
#            
#            properties = []
#            parameters = dict()
#            attributes = {'name':name,'input':inp,'output':outp,'icon':icon,'libname':libname} 
#            
#            data = getSymbolData(attributes,properties,parameters)
#            
#            self.path = os.getcwd()            
#            f = open(self.path + '/libraries/library_' + libname + '/' + name + '.py','w+')
#            f.write(str(data))
#            f.close()
#            
#            i = self.parent.tabs.currentIndex()
#            self.parent.symbolView()
#            self.parent.tabs.setCurrentIndex(i)
        
        
        
        
    def editPins(self):
        self.parent.editPins(self.actComp)
#        block = self.actComp
#        inputs, outputs, inouts = block.pins()
#        d = txtDialog('Pins of {}'.format(block.name))
#        pinlist = d.editList(inputs + outputs + inouts, header='io x y name')
#        if pinlist:
#            for p in block.ports():
#                p.setParentItem(None) # effectively removing port
#                
#            block.inp  = []
#            block.outp = []
#            for tp, x, y, name in pinlist:
#                if tp == 'i':
#                    block.add_inPort([name, x, y])
#                    block.inp.append([name, x, y])
#                elif tp == 'o':
#                    block.add_outPort([name, x, y])
#                    block.outp.append([name, x, y])
#                else:
#                    print('{} is not an implemented io type'.format(tp))
#            block.update()

    def editIcon(self):
        self.parent.editIcon(self.actComp)
#        '''edit svg file'''
#        block = self.actComp
#        #blockname = block.name
#        svgiconname = os.path.join(respath, 'blocks', block.icon+'.svg')
#        #svgfilename = os.path.join(respath, 'blocks', blockname+'.svg')
#        with open(svgiconname) as fi:
#            t = fi.read()
#        #generate a tempfile
#        fo = tempfile.NamedTemporaryFile(suffix='.svg', delete=False)
#        svgtempfilename = fo.name
#        fo.write(t)
#        fo.close()
#
#        try:
#            timestamp0 = os.stat(svgtempfilename).st_mtime
#            subprocess.call('inkscape {}'.format(svgtempfilename).split())
#            timestamp1 = os.stat(svgtempfilename).st_mtime
#            if  timestamp0 < timestamp1: # newer => copy'
#                shutil.move(svgtempfilename, svgiconname)
#                block.setIcon()
#                
#            # creanup tempfile
#            if os.path.exists(svgtempfilename):
#                os.remove(svgtempfilename)
#                
#        except OSError:
#            raise Exception('Inkscape is not installed')
        
        
        

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
        
        
        
def getSymbolData(attributes,properties,parameters):
    name = attributes['name']
    libname = attributes['libname']
    inp = attributes['input']
    outp = attributes['output']
    icon = attributes['icon']
        
#\n\
#def getDiagram():\n\
#    fname = 'libraries.' + libname + '.' + name + '_diagram'\n\
#    exec('import ' + fname)\n\
#    reload(eval(fname))\n\
#\n\
#    items = eval(fname + '.items')\n\
#\n\
#    return items\n\
#\n\
#def getText():\n\
#    fname = 'libraries/' + libname + '/' + name + '.py'\n\
#    f = open(fname,'r')\n\
#    content = f.read()\n\
#    f.close()\n\
#    return content\n\
#\n\
    template = "name = '{name}' #zelfde als bestand naam \n\
libname = '{libname}' #zelfde als map naam\n\
\n\
inp = {inp}\n\
outp = {outp}\n\
\n\
parameters = {parameters} #parametriseerbare cell\n\
properties = {properties} #voor netlisten\n\
\
\
#view variables:\n\
iconSource = '{icon}'\n\
textSource = 'libraries/library_{libname}/{name}.py'\n\
\n\
\n\
views = {{'icon':iconSource,'text':textSource}}"
    return template.format(name=name,libname=libname,inp=str(inp),outp=str(outp),properties=str(properties),parameters=str(parameters),icon=str(icon))

        
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
                                                
                                                
        
        self.addLibraryAction = QtWidgets.QAction(QtGui.QIcon(mypath+'addLibrary.png'),
                                                '&Add Library', self,
                                                triggered = self.addLibrary)   
        
        self.toolbar = self.addToolBar('File')
        self.toolbar.addAction(self.listViewAction)
        self.toolbar.addAction(self.symbolViewAction)  
        self.toolbar.addAction(self.addLibraryAction)  
        
        
    def addLibrary(self):
        dialog = textLineDialog('Name: ')
        ret = dialog.getLabel()
        if ret:
            try:
                path = os.getcwd()
                os.mkdir(path + '/libraries/library_' + ret)
                
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
                
                file = open(path + '/libraries/library_' + ret + '/__init__.py', 'w+')
                file.close()
            except:
                error('Library already exists')
    
    
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
        
        if actComp:
            blockname = actComp.blockname
            libname = actComp.libname
        else:
            libname = self.libraries.currentItem().text()
            blockname = self.cells.currentItem().text()
        
        source = libraries.getViews(blockname,libname)[type]
        editor = viewEditors[type]
        print(source,editor)
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
        libnames = sorted(self.libs.keys(), key=lambda s: s.lower())
        self.libraries.addItems(libnames)
         
        
        self.layout = QtWidgets.QHBoxLayout(self.centralWidget)
        
        self.layout.addWidget(self.libraries)
        #self.layout.addWidget(self.catogories)
        self.layout.addWidget(self.cells)
        self.layout.addWidget(self.views)
        
        self.setCentralWidget(self.centralWidget)
        
        self.cells.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.cells.customContextMenuRequested.connect(self.onContext)
        
        self.cells.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.cells.customContextMenuRequested.connect(self.onContext)
        
        
        self.libraries.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.libraries.customContextMenuRequested.connect(self.onContextLib)
        
    
    def removeBlock(self,actComp):
        if self.type == 'symbolView':
            blockname = actComp.blockname
            libname = actComp.libname
        else:
            libname = self.libraries.currentItem().text()
            blockname = self.cells.currentItem().text()
        
        path = os.getcwd()
        
        filenames = []
        views = libraries.getViews(blockname,libname)
        for key in views.keys():
            if key != 'icon':
                filenames.append(views[key])
        for filename in filenames:
            try:
                binName = filename.replace('libraries/library_' + libname,'')
                os.rename(path + '/' + filename,path + '/libraries/bin' + binName)
            except:
                error('View not found')
            try:
                os.remove(path + '/' + filename + 'c')
            except:
                pass        
        
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
    
    def onContextLib(self,point):
        self.menuLibrary = QtWidgets.QMenu()
        
        
        createIconAction = self.menuLibrary.addAction('Create block')
        createIconAction.triggered.connect(self.createBlock)
        
        
        self.pasteBlockAction   = self.menuLibrary.addAction('Paste')
        self.pasteBlockAction.triggered.connect(self.pasteBlock)
        self.menuLibrary.exec_(self.libraries.mapToGlobal(point))
        
    def onContext(self,point):
        if self.libraries.currentItem() and self.cells.currentItem():
            menuBlk = QtWidgets.QMenu()
            
            # create context menu
            editIconAction   = menuBlk.addAction('edit Icon')
            editIconAction.triggered.connect(self.editIcon)
    
            editPinsAction   = menuBlk.addAction('Edit pins')
            editPinsAction.triggered.connect(self.editPins)
            
            
            cutBlockAction   = menuBlk.addAction('Cut')
            cutBlockAction.triggered.connect(self.cutBlock)
            
            changeIconAction = menuBlk.addAction('Change icon')
            changeIconAction.triggered.connect(self.changeIcon)
            
            
            removeBlockAction = self.menuBlk.addAction('Remove block')
            removeBlockAction.triggered.connect(self.removeBlock)
            
            
            
            viewMenu = QtWidgets.QMenu("Views")
            
            menuBlk.addMenu(viewMenu)
            
            
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
                    action = viewMenu.addAction(key+" view")
                    action.triggered.connect(viewAction)
            menuBlk.exec_(self.cells.mapToGlobal(point))
        else:
            self.menuLibrary = QtWidgets.QMenu()
            
            
            createIconAction = self.menuLibrary.addAction('Create block')
            createIconAction.triggered.connect(self.createBlock)
            
            
            self.pasteBlockAction   = self.menuLibrary.addAction('Paste')
            self.pasteBlockAction.triggered.connect(self.pasteBlock)
            self.menuLibrary.exec_(self.cells.mapToGlobal(point))

    def pasteBlock(self):
        if self.copiedBlock and self.copiedBlockLibname:
            path = os.getcwd()
            if self.type == 'symbolView':
                libname = self.tabs.tabText(self.tabs.currentIndex())
            else:
                if self.libraries.currentItem():
                    libname = self.libraries.currentItem().text() 
                else:
                    return
                    
            if libname != self.copiedBlockLibname:
                filenames = []
                views = libraries.getViews(self.copiedBlock,self.copiedBlockLibname)
                for key in views.keys():
                    if key != 'icon':
                        filenames.append(views[key])
                for filename in filenames:
                    newFilename = filename.replace('libraries/library_' + self.copiedBlockLibname,'libraries/library_' + libname)
                    os.rename(path + '/' + filename,path + '/' + newFilename)
                    try:
                        os.remove(path + '/' + filename + 'c')
                    except:
                        pass
                    
                    
                #change sources
                    
                path = os.getcwd()
                fname = '/libraries/library_{}/{}.py'.format(libname,self.copiedBlock)
                f = open(path + fname,'r')
                lines = f.readlines()
                f.close()
                
                for index,line in enumerate(lines):
                    lines[index] = line.replace('libraries/library_' + self.copiedBlockLibname,'libraries/library_' + libname)
                    
                
                
                f = open(path + fname,'w+')
                f.write("".join(lines))
                f.close()    
                    
                
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

    def createBlock(self):
        if self.type == 'symbolView':
            libname = self.tabs.tabText(self.tabs.currentIndex())
        else:
            if self.libraries.currentItem():
                libname = self.libraries.currentItem().text() 
            else:
                return
        
        dialog = createBlockDialog()
        
        ret = dialog.getRet()
        
        if ret:
            name = ret['name']
            inp = ret['input']
            outp = ret['output']
            icon = ret['icon']
            
            properties = ret['properties']
            parameters = ret['parameters']
            attributes = {'name':name,'input':inp,'output':outp,'icon':icon,'libname':libname} 
            
            data = getSymbolData(attributes,properties,parameters)
            
            self.path = os.getcwd()            
            f = open(self.path + '/libraries/library_' + libname + '/' + name + '.py','w+')
            f.write(str(data))
            f.close()
            
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


    def editIcon(self,actComp=None):
        '''edit svg file'''
        if self.type == 'symbolView':
            block = actComp
        else:
            libname = self.libraries.currentItem().text()
            blockname = self.cells.currentItem().text()
            block = libraries.getBlock(blockname,libname)
            block.setup()
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

    def editPins(self,actComp=None):
        if self.type == 'symbolView':
            block = actComp
        else:
            libname = self.libraries.currentItem().text()
            blockname = self.cells.currentItem().text()
            block = libraries.getBlock(blockname,libname)
            block.setup(scene=None)
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

    def cutBlock(self,actComp=None):
        if self.type == 'symbolView':
            self.copiedBlock = actComp.blockname
            self.copiedBlockLibname = actComp.libname
        else:
            self.copiedBlockLibname = self.libraries.currentItem().text()
            self.copiedBlock = self.cells.currentItem().text()
            
    def changeIcon(self,actComp=None):
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open',respath + '/blocks/', filter='*.svg')
        if filename[0]:
            icon = QtCore.QFileInfo(filename[0]).baseName()
            path = os.getcwd()
            if self.type == 'symbolView':
                libname = actComp.libname
                blockname = actComp.blockname
            else:
                libname = self.libraries.currentItem().text()
                blockname = self.cells.currentItem().text()
            fname = '/libraries/library_{}/{}.py'.format(libname,blockname)
            f = open(path + fname,'r')
            lines = f.readlines()
            f.close()
            
            for index,line in enumerate(lines):
                if line.startswith('iconSource = '):
                    lines[index] = "iconSource = '{}'\n".format(icon)
            
            
            f = open(path + fname,'w+')
            f.write("".join(lines))
            f.close()  
            
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
    
    def symbolView(self):
        self.copiedBlock = None
        self.copiedBlockLibname = None
        
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
#            if libname == 'symbols':
#                self.symbolTab = tab
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
            cellList = sorted(self.libs[library.text()], key=lambda s: s.lower())
            for cell in cellList:
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
