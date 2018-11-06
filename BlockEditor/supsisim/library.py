# -*- coding: utf-8 -*-
"""
"""
# aim for python 2/3 compatibility
from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

from  Qt import QtGui, QtWidgets, QtCore # see https://github.com/mottosso/Qt.py

import os, sys
from lxml import etree

import tempfile
import subprocess
import shutil

import libraries
from supsisim.svg_utils import updateSvg

from supsisim.const import DB, respath, viewTypes

from supsisim.block import Block, getBlock, getBlockModule, getViews, \
                           saveBlock, rmBlock, calcBboxFromPins, gridPos
                            
from supsisim.dialg import txtDialog, \
                           textLineDialog, createBlockDialog, error, \
                           addViewDialog, editPinsDialog
          


class CompViewer(QtWidgets.QGraphicsScene):
    '''mini diagram used in symbolView tabs'''
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

        createBlockAction = self.menuLibrary.addAction('Create block')
        createBlockAction.triggered.connect(self.parent.createBlock)

        editPinsAction   = self.menuBlk.addAction('Edit pins')
        editPinsAction.triggered.connect(self.editPins)
        
        
        editBboxAction   = self.menuBlk.addAction('Change Bbox')
        editBboxAction.triggered.connect(self.editBbox)
        
        
        cutBlockAction   = self.menuBlk.addAction('Cut')
        cutBlockAction.triggered.connect(self.cutBlock)
        
        changeIconAction = self.menuBlk.addAction('Change icon')
        changeIconAction.triggered.connect(self.changeIcon)
        
        
        removeBlockAction = self.menuBlk.addAction('Remove block')
        removeBlockAction.triggered.connect(self.removeBlock)
        
        
#        reCreateIconAction = self.menuBlk.addAction('(re)create icon')
#        reCreateIconAction.triggered.connect(self.createIcon)
        
        
        self.pasteBlockAction   = self.menuLibrary.addAction('Paste')
        self.pasteBlockAction.triggered.connect(self.parent.pasteBlock)
        
        self.viewMenu = QtWidgets.QMenu("Views")
        
        self.menuBlk.addMenu(self.viewMenu)

    def addViewAction(self):
        self.parent.addViewAction(self.actComp)

    def addViewMenu(self):
        views = getViews(self.actComp.libname, self.actComp.blockname)
        for key in views.keys():
            if key != 'diagram' and key != 'icon':
                def getFunction(key):
                    def viewAction():
                        self.parent.openView(key, self.actComp)
                    return viewAction
                viewAction = getFunction(key)
                action = self.viewMenu.addAction(key+" view")
                action.triggered.connect(viewAction)

    def changeIcon(self):
        self.parent.changeIcon(self.actComp)
        
    def contextMenuEvent(self, event):
        pos = gridPos(event.scenePos())
        for item in self.items(QtCore.QRectF(pos-QtCore.QPointF(DB,DB), QtCore.QSizeF(2*DB,2*DB))):
            if isinstance(item, Block):
                self.viewMenu.clear()
                self.addViewMenu()
                
                addViewAction = self.viewMenu.addAction("Add view")
                addViewAction.triggered.connect(self.addViewAction)
                self.menuBlk.exec_(event.screenPos())
                break
        else:
            if self.parent.copiedBlock and self.parent.copiedBlockLibname:
                self.pasteBlockAction.setEnabled(True)
            else:
                self.pasteBlockAction.setEnabled(False)
            self.menuLibrary.exec_(event.screenPos())

    def cutBlock(self):
        self.parent.cutBlock(self.actComp)

    def editBbox(self):
        self.parent.editBbox(self.actComp)
    
    def editIcon(self):
        self.parent.editIcon(self.actComp)

    def editPins(self):
        self.parent.editPins(self.actComp)

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton and isinstance(self.actComp, Block):
            mimeData = QtCore.QMimeData()
            block = self.actComp
#            attributes = {'name':c.name,'input':c.inp,'output':c.outp,'icon':c.icon,'flip':c.flip,'libname':c.libname,'type':c.type}
#            data = '@'.join([str(attributes),str(c.parameters),str(c.properties),c.blockname,c.libname])
            data = '@'.join([block.libname,block.blockname])
            mimeData.setText(data)
            drag = QtGui.QDrag(self.parent)
            drag.setMimeData(mimeData)
            drag.exec_(QtCore.Qt.CopyAction)

    def mousePressEvent(self, event):
        pos = gridPos(event.scenePos())
        for item in self.items(QtCore.QRectF(pos-QtCore.QPointF(DB,DB), QtCore.QSizeF(2*DB,2*DB))):
            if isinstance(item, Block):
                self.actComp = item
     
    def mouseReleaseEvent(self, event):
        pass

    def removeBlock(self):
        self.parent.removeBlock(self.actComp)
    
    def setUniqueName(self, block):
        '''should returns a unique name, but this is the only occurence (in the library viewer)'''
        return block.name 
        
class Library(QtWidgets.QMainWindow):
    '''
    '''
    def __init__(self,parent=None):
        super(Library, self).__init__(parent)

        self.resize(800, 500)
        self.setWindowTitle('Library')
        self.libConfig = ()
#        self.readLib()
        self.addToolbars()
        self.closeFlag = False
        
        # set to symbolview mode
        self.symbolView()

    def getnames(self, actComp=None):
            if actComp and self.type == 'symbolView':
                libname = actComp.libname
                blockname = actComp.blockname
            else:
                libname = self.libraries.currentItem().text()
                blockname = self.cells.currentItem().text()

            fname = os.path.join(os.getcwd(),'libraries', 'library_'+libname, blockname+'.py')
            return libname, blockname, fname, getBlockModule(libname, blockname)

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
        
    
    def editBbox(self,actComp=None):
        
        if actComp:
            blockname = actComp.blockname
            libname = actComp.libname
            blk = actComp
            cx, cy, w, h = blk.center.x(), blk.center.y(), blk.w, blk.h
            bbox = (int(cx - w/2), int(cy - h/2), int(w), int(h))
            
        else:
            libname = self.libraries.currentItem().text()
            blockname = self.cells.currentItem().text()
            blk = getBlockModule(blockname,libname)
            bbox = blk.bbox if 'bbox' in blk.__dict__ else None
            if bbox is None:
                bbox = calcBboxFromPins(blk.inp, blk.outp)
        
        if 'getSymbol' in blk.__dict__:
            error("you have to change the getSymbol function to change this block's bbox")
            return
             
        x0, y0, w, h = bbox
        x1, y1 = x0+w, y0+h
        lines =  [('left',   int(x0)), 
                  ('top',    int(y0)), 
                  ('right',  int(x1)),
                  ('bottom', int(y1))]

        dialog = txtDialog()       
        ret = dialog.editList(lines)
        
        if ret:
            d = dict(ret)
            x0, y0, x1, y1 = d['left'], d['top'], d['right'], d['bottom']
            bbox = (x0, y0, x1-x0, y1-y0)
            libname, blockname, fname, blk = self.getnames(actComp)
            dd = dict()
            dd['bbox'] = bbox
            src = libraries.updateSource(libname, blockname, dd)
            if 'bbox' not in src:
                lines = src.splitlines()
                for ix, line in enumerate(lines):
                    if line.startswith('outp'):
                        line[ix] = line[ix] + 'bbox = {}\n'.format(bbox)
                        break
                src = ''.join(lines)
                with open(fname, 'wb') as f:
                    f.write(src)
                reload('libraries.library_{}.{}'.format(libname, blockname))
            
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
    
    def addLibrary(self):
        dialog = textLineDialog('Name: ','Add library')
        ret = dialog.getLabel()
        if ret:
            try:
                # create path
                fp = libraries.libpath(ret)
                os.mkdir(fp)
                # create __init__.py
                f = open(os.path.join(fp, '__init__.py', 'w+'))
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
                
            except:
                error('Library already exists')
    
    
    def switchToListView(self):
        mypath = respath + '/icons/'
        textViewAction = QtWidgets.QAction(QtGui.QIcon(mypath+'textIcon.png'),
                                                '&text view', self,
                                                triggered = self.textView)             
        
        self.toolbar.addAction(textViewAction)    
        self.listView()
    
    def openView(self, viewtype, actComp=None):
        
        if actComp:
            blockname = actComp.blockname
            libname = actComp.libname
        else:
            libname = self.libraries.currentItem().text()
            blockname = self.cells.currentItem().text()
        
        try:
            source = getViews(libname,blockname)[viewtype]
        except:
            error('view not found')
            
        cmd = None
        for tp, (editor, extension) in viewTypes.items():
            if source.endswith(extension):
                cmd = editor
                break
        if cmd:
            os.system(cmd + " " + source)
        else:
            error("{} is unkown type\nplease see viewTypes in menu Settings -> Edit settings".format(source))
            return
            
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
               
    def listView(self):
        '''switch to listView'''
        self.type = 'listView'
        reload(libraries)
        self.centralWidget = QtWidgets.QWidget()
          
        self.libraries = QtWidgets.QListWidget(self.centralWidget)
        #self.categories = QtWidgets.QListWidget(self.centralWidget)
        self.cells = QtWidgets.QListWidget(self.centralWidget)
        self.views = QtWidgets.QListWidget(self.centralWidget)
        
        self.libraries.currentItemChanged.connect(self.clickLibrary)
        #self.categories.currentItemChanged.connect(self.clickCatogory)
        self.cells.currentItemChanged.connect(self.clickCell)
        self.views.currentItemChanged.connect(self.clickView)
        
        
        # fill libs column
        self.libs = libraries.libs
        libnames = sorted(self.libs.keys(), key=lambda s: s.lower())
        self.libraries.addItems(libnames)
         
        
        self.layout = QtWidgets.QHBoxLayout(self.centralWidget)
        
        self.layout.addWidget(self.libraries)
        #self.layout.addWidget(self.categories)
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
        
        rmBlock(libname, blockname)
        
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
        
        
        createBlockAction = self.menuLibrary.addAction('Create block')
        createBlockAction.triggered.connect(self.createBlock)
        
        
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
            
            
            editBboxAction   = menuBlk.addAction('Change Bbox')
            editBboxAction.triggered.connect(self.editBbox)
            
            
            cutBlockAction   = menuBlk.addAction('Cut')
            cutBlockAction.triggered.connect(self.cutBlock)
            
            changeIconAction = menuBlk.addAction('Change icon')
            changeIconAction.triggered.connect(self.changeIcon)
            
            
            removeBlockAction = menuBlk.addAction('Remove block')
            removeBlockAction.triggered.connect(self.removeBlock)
            
            
            
            viewMenu = QtWidgets.QMenu("Views")
            
            menuBlk.addMenu(viewMenu)
            
            
            libname = self.libraries.currentItem().text()
            blockname = self.cells.currentItem().text()
            views = getViews(libname, blockname)
            for key in views.keys():
                if key != 'diagram' and key != 'icon':
                    def getFunction(key):
                        def viewAction():
                            self.openView(key)
                        return viewAction
                    viewAction = getFunction(key)
                    action = viewMenu.addAction(key+" view")
                    action.triggered.connect(viewAction)
            addViewAction = viewMenu.addAction("Add view")
            addViewAction.triggered.connect(self.addViewAction)
                    
            menuBlk.exec_(self.cells.mapToGlobal(point))
        else:
            self.menuLibrary = QtWidgets.QMenu()
            
            
            createBlockAction = self.menuLibrary.addAction('Create block')
            createBlockAction.triggered.connect(self.createBlock)
            
            
            self.pasteBlockAction   = self.menuLibrary.addAction('Paste')
            self.pasteBlockAction.triggered.connect(self.pasteBlock)
            self.menuLibrary.exec_(self.cells.mapToGlobal(point))
    
#    def addView(self, blockname, libname, type, viewSource):
#        blk = getBlock(libname, blockname)    
#        dd = dict()
#        if type == 'icon':
#            dd[type+'Source'] = viewSource
#        blk.views[type+'Source'] = viewSource
#        dd['views'] = blk.views
#        
#        libraries.updateSource(libname, blockname, dd)
    
    def addViewAction(self,actComp=None):
        libname, blockname, fname, blk = self.getnames(actComp)
        dialog = addViewDialog(libname,blockname)
        ret = dialog.getRet()
        if ret:
            try:
                path = os.getcwd()
                f = open(path + "/" + ret[1],'w+')
                f.close()
            except:
                error('File source not correct')
                return
                
            self.actComp.addView(ret[0],ret[1])
            
            self.openView(ret[0], actComp)
            
    
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
                views = libraries.getViews(self.copiedBlockLibname, self.copiedBlock)
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
                
#                for index,line in enumerate(lines):
#                    lines[index] = line.replace('libraries/library_' + self.copiedBlockLibname,'libraries/library_' + libname)
                    
                
                
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
            blockname = ret['name']
            pins = [ret['input'], ret['output'], ret['io']]
            icon = ret['icon']
            
            properties = ret['properties']
            parameters = ret['parameters']
            
            saveBlock(libname, blockname, pins, icon, bbox=None, properties=properties, parameters=parameters)
            
            # update libary viewer
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
            block = getBlock(libname, blockname)

        svgiconname = block.icon #  = svgfilepath
        if svgiconname is None:
            svgiconname = libraries.blockpath(libname, blockname).rstrip('.py') + '.svg'
        
        # temp file
        fo = tempfile.NamedTemporaryFile(suffix='.svg', delete=False)
        svgtempfilename = fo.name

        if os.path.isfile(svgiconname):
            with open(svgiconname) as fi:
                t = fi.read()
            
            #copy to a tempfile
            fo.write(t)
            fo.close()
        
        updateSvg(block, svgtempfilename)
            
        timestamp0 = os.stat(svgtempfilename).st_mtime

        try:
            subprocess.call('inkscape {}'.format(svgtempfilename).split())
            timestamp1 = os.stat(svgtempfilename).st_mtime
            
                
            if timestamp0 and timestamp0 < timestamp1: # newer => copy and update
                print('scrubbing', svgtempfilename)
                updateSvg(block, svgtempfilename, makeports=False)
                if not svgiconname.lower().endswith('.svg'): # old-style icon
                    svgiconname = libraries.blockpath(block.libname, block.blockname).rstrip('.py') + '.svg'
                shutil.move(svgtempfilename, svgiconname)
                print('mv to', svgiconname)
                block.setIcon(svgiconname)
                # register niew view
                block.setView('icon', svgiconname)
                
            # creanup tempfile
            if os.path.exists(svgtempfilename):
                os.remove(svgtempfilename)
                
        except OSError:
            raise Exception('Inkscape is not installed')


    def editPins(self,actComp=None):
        libname, blockname, fname, blk = self.getnames(actComp)
        if 'getSymbol' in blk.__dict__:
            error('cannot edit parametrized cell, the pins should be set in getSymbol')
        if 'diagram' in getViews(libname, blockname):
            error('Cannot edit pins of block that has a diagram')
            return
        
        inp = blk.inp
        outp = blk.outp
        
        dialog = editPinsDialog(inp,outp)
        ret = dialog.getRet()
        if ret:
            dd = dict()
            dd['inp'] = ret[0]
            dd['outp'] = ret[1]
            
            
            libraries.updateSource(libname, blockname, dd)
            
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

    def cutBlock(self,actComp=None):
        if self.type == 'symbolView':
            self.copiedBlock = actComp.blockname
            self.copiedBlockLibname = actComp.libname
        else:
            self.copiedBlockLibname = self.libraries.currentItem().text()
            self.copiedBlock = self.cells.currentItem().text()
            
    def changeIcon(self, actComp=None):
        libname, blockname, fname, blk = self.getnames(actComp)
        path = libraries.libpath(libname)
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open', path, filter='*.svg')
        if filename:
            # strip absolute path if in same dir as block itself
            actComp.setIcon(filename)

            if os.path.dirname(filename) == libraries.libpath(libname):
                filename = os.path.basename(filename)

            actComp.setView('icon', filename)
            
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
        self.tabs = QtWidgets.QTabWidget()
        self.quickSelTab = QtWidgets.QComboBox()
        
        libs = libraries.libs
        # case insensitive sorting
        libnames = sorted(libs.keys(), key=lambda s: s.lower())
        self.quickSelTab.addItems(libnames)
        for libname in libnames:
            
            lib = libs[libname]
            diagram = CompViewer(self)
            diagram.clear()
            view = QtWidgets.QGraphicsView(diagram)
            diagram.compLock = True
            for i, blockname in enumerate(lib):
                # add block to diagram
                block = getBlock(libname, blockname, scene=diagram)
                if block:
                    px = i % 2
                    py = i/2
                    block.scene = diagram
                    block.setPos(px*150,py*150)
#                    block.setup()
                    w = block.boundingRect().width()
                    h = block.boundingRect().height()
                    if h > 100 or w > 80:
                        scale = min(1.0, 80.0/w, 100.0/h)
                        # keep label readable
                        set_orient(block, scale=scale)
                        block.label.scale = 1.0/scale
                        block.label.setNormal() # normal orientation, but will also set scale
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
        category = self.categories.currentItem().text()
        
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
        pos = gridPos(event.scenePos())
        item = self.itemAt(pos)
        if isinstance(item, Block):
            self.menuBlk.exec_(event.screenPos())
        else:
            pass

def set_orient(item, flip=False, scale=0, rotate=0, combine=False):
    '''returns QTransform, operation order: flip (mirror in Y axis), scale, rotate (in degrees)'''
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
