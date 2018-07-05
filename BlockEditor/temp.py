# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import testSaveFile

print(testSaveFile.items)

#import sys
#from Qt import QtWidgets,QtCore,QtGui
#
#class Block(QtWidgets.QGraphicsPathItem):
#    def __init__(self,parent , scene):
#        self.scene = scene
#        if QtCore.qVersion().startswith('5'):
#            super(Block, self).__init__(parent)
#            if self.scene:
#                self.scene.addItem(self)
#        else:
#            super(Block, self).__init__(parent, self.scene)
#            
#        p = QtGui.QPainterPath()
#        
#        p.addRect(-10, -10, 10, 10)
#
#        self.setPath(p)
#        self.setFlag(self.ItemIsMovable)
#
#class mainWindow(QtWidgets.QMainWindow):
#    def __init__(self,name):
#        super(mainWindow, self).__init__()
#        self.centralWidget = QtWidgets.QWidget(self)
#        self.setCentralWidget(self.centralWidget)
#        self.setWindowTitle(name)
#        
#        self.scene = QtWidgets.QGraphicsScene()
#        self.view = QtWidgets.QGraphicsView(self.scene,self)
#        self.view.setGeometry(10,10,200,200)
#        self.scene2 = QtWidgets.QGraphicsScene()
#        self.view2 = QtWidgets.QGraphicsView(self.scene2,self)
#        self.view2.setGeometry(210,210,200,200)
#        b1 = Block(None,self.scene)
#        b2 = Block(b1,self.scene)
#        b2.setPos(10,10)
#
#app = QtWidgets.QApplication(sys.argv)
#
#main = mainWindow('hoi')
#main.setGeometry(500,100,1024,768)
#main.show()
##extra = mainWindow('2?')
##extra.setGeometry(10,10,1024,768)
##extra.show()
#ret = app.exec_()
#app.deleteLater()