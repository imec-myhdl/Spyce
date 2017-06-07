#!/usr/bin/python

import sys
if sys.version_info>(3,0):
    import sip
    sip.setapi('QString', 1)
from PyQt4 import QtGui, QtCore
#import dircache
import os

from supsisim.block import Block
from supsisim.const import respath
from lxml import etree

class CompViewer(QtGui.QGraphicsScene):
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

        t = QtGui.QTransform()
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
            drag = QtGui.QDrag(self.parent)
            drag.setMimeData(mimeData)
            drag.exec_(QtCore.Qt.CopyAction)

    def mouseReleaseEvent(self, event):
        pass
        
class Library(QtGui.QMainWindow):
    '''
    '''

    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)

        self.centralWidget = QtGui.QWidget()
        self.resize(800, 500)
        self.setWindowTitle('Library')
        self.libConfig = ()
        self.readLib()
        self.closeFlag = False

        self.tabs = QtGui.QTabWidget()

        for p in self.libConfig:
            diagram = CompViewer(self)
            view = QtGui.QGraphicsView(diagram)
            diagram.compLock = True

            for i in range(1, len(p)):
                io = (p[i][3] == 1)
                b = Block(None, diagram, p[i][0], p[i][1], p[i][2], io, p[i][4], p[i][5], False)
                px = (i-1) % 2
                py = (i-1)/2
                b.setPos(px*150,py*150)

            tab = QtGui.QWidget()
            layout = QtGui.QVBoxLayout()
            layout.addWidget(view)
            tab.setLayout(layout)

            self.tabs.addTab(tab, p[0])

        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.tabs)
        self.widget = QtGui.QWidget()
        self.widget.setLayout(layout)
        self.setCentralWidget(self.widget)
        self.tabs.setCurrentIndex(2)
        
    def readLib(self):
        files = os.listdir(respath+'blocks/')
        for f in sorted(files):
            if f.endswith('.blk'):
                tree = etree.parse(respath +'blocks/' + f)
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
    app = QtGui.QApplication(sys.argv)

    library = Library()
    library.setGeometry(20, 20, 400, 500)
    library.show()

    app.exec_()
    sys.exit()
