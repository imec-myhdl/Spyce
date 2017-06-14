#!/usr/bin/python

import sys
#if sys.version_info>(3,0):
#    import sip
#    sip.setapi('QString', 1)

from pyqt45 import QGraphicsScene, QMainWindow, QWidget, QVBoxLayout, \
                   QHBoxLayout, QGraphicsView,QTabWidget, QApplication, \
                   QTransform, QDrag, QtCore, set_orient

#import dircache
import os

from supsisim.block import Block
from supsisim.const import respath
from lxml import etree

from  supsisim import imeclib

class CompViewer(QGraphicsScene):
    def __init__(self, parent=None):
        super(CompViewer, self).__init__()
        self.parent = parent

        self.componentList = []	 
        self.activeComponent = None 

    def setUniqueName(self, block):
        return block.name
        
    def dropEvent(self, event):
        event.accept()

    def dragEnterEvent(self, event):
        event.accept()

    def dragMoveEvent(self, event):
        event.accept()

    def mousePressEvent(self, event):
        x = event.scenePos().x()
        y = event.scenePos().y()

        t = QTransform()
        self.actComp = self.itemAt(x, y, t)

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton and isinstance(self.actComp, Block):
            mimeData = QtCore.QMimeData()
            if self.actComp.iosetble:
                io = '1'
            else:
                io = '0'
            data = self.actComp.name+'@'+self.actComp.inp.__str__()+'@'+self.actComp.outp.__str__() + '@' + io +'@' + self.actComp.icon + '@' + self.actComp.params
            mimeData.setText(data)
            drag = QDrag(self.parent)
            drag.setMimeData(mimeData)
            drag.exec_(QtCore.Qt.CopyAction)

    def mouseReleaseEvent(self, event):
        pass
        
class Library(QMainWindow):
    '''
    '''

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.centralWidget = QWidget()
        self.resize(800, 500)
        self.setWindowTitle('Library')
        self.libConfig = ()
#        self.readLib()
        self.closeFlag = False

        self.tabs = QTabWidget()
        
        libs = imeclib.libs
        for libname in sorted(libs.keys(), key=lambda s: s.lower()): # case insensitive sorting
            lib = libs[libname]
            diagram = CompViewer(self)
            view = QGraphicsView(diagram)
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
                    set_orient(cell, scale=min(1.0, 80/w, 100.0/h))
            tab = QWidget()
            layout = QVBoxLayout()
            layout.addWidget(view)
            tab.setLayout(layout)

            self.tabs.addTab(tab, libname)
            
                

#        for p in self.libConfig:
#            diagram = CompViewer(self)
#            view = QGraphicsView(diagram)
#            diagram.compLock = True
#
#            for i in range(1, len(p)):
#                io = (p[i][3] == 1)
#                b = Block(None, diagram, p[i][0], p[i][1], p[i][2], io, p[i][4], p[i][5], False)
#                px = (i-1) % 2
#                py = (i-1)/2
#                b.setPos(px*150,py*150)
#                print 'debug',p[0], repr(b)
#
#            tab = QWidget()
#            layout = QVBoxLayout()
#            layout.addWidget(view)
#            tab.setLayout(layout)
#
#            self.tabs.addTab(tab, p[0])

        layout = QHBoxLayout()
        layout.addWidget(self.tabs)
        self.widget = QWidget()
        self.widget.setLayout(layout)
        self.setCentralWidget(self.widget)
        self.tabs.setCurrentIndex(2)
        
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

if __name__ == '__main__':
    import sys
    import logging
    logging.basicConfig()
    app = QApplication(sys.argv)

    library = Library()
    library.setGeometry(20, 20, 400, 500)
    library.show()

    app.exec_()
    sys.exit()
