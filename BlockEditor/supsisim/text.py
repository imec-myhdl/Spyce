# -*- coding: utf-8 -*-
"""
TextItem Class
"""
from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

from  Qt import QtGui, QtWidgets, QtCore # see https://github.com/mottosso/Qt.py
from collections import OrderedDict

#from supsisim.const import iconFont
from supsisim.const import colors

class textItem(QtWidgets.QGraphicsTextItem):
    '''convenience class, extension of QGraphicsTextItem, that realises aligned text
    textItem.setFlipped() will mirror the text  (in place)
    textItem.setNormal() will put txt in normal (non-mirrored) state
    
    anchor is (look at numpad):
    1: bottom-left
    2: bottom-center
    3: bottom-right
    4: center-left
    5: center-center
    6: center-right
    7: top-left
    8: top-center
    9: top-right'''
    def __init__(self, text, anchor=1, parent=None):
        super(textItem, self).__init__(text, parent)
        self.anchor = anchor
        self.scale = 1
#        self.setFont(iconFont)
        
        # compute dx, dy absed on anchor
        self.setAnchor()
        self.setNormal()
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemIsSelectable)
#        self.setFlag(self.ItemIgnoresTransformations)
        self.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        self.setAcceptDrops(False)

    def toData(self):
        data = OrderedDict(type='label')
        data['text']   = self.toPlainText()
        data['x'] = self.pos().x()
        data['y'] = self.pos().y()
        data['anchor'] = self.anchor
        return data

    def fromData(self, d):
        self.setPlainText(d['text'])
        self.setPos(d['x'], d['y'])
        self.setAnchor(d['anchor'])
        self.setNormal()
        
    def setFlipped(self):
        '''mirror in place (use when parent is flipped'''
        self.setTransform(QtGui.QTransform().translate(self.dx, self.dy).scale(-self.scale,self.scale).translate(-self.boundingRect().width(),0))
        self.setAnchor()
        self.setTransform(QtGui.QTransform().translate(self.dx, self.dy).scale(-self.scale,self.scale).translate(-self.boundingRect().width(),0))

    def setNormal(self):
        '''normal orientation'''
        self.setTransform(QtGui.QTransform.fromScale(self.scale,self.scale).translate(self.dx, self.dy))
        self.setAnchor()
        self.setTransform(QtGui.QTransform.fromScale(self.scale,self.scale).translate(self.dx, self.dy))
        
    def setAnchor(self, anchor=None):
        if anchor:
            self.anchor = anchor
        if self.anchor in (4,5,6):
            self.dy = -0.5*self.boundingRect().height()
        elif self.anchor in (1,2,3):
            self.dy = -self.boundingRect().height()
        else:
            self.dy = 0

        if self.anchor in (2,5,8):
            self.dx = -0.5*self.boundingRect().width()
        elif self.anchor in (3,6,9):
            self.dx = -self.boundingRect().width()
        else:
            self.dx = 0

class Comment(textItem):
    def __init__(self, text, anchor=1, parent=None):
        super(Comment, self).__init__(text, anchor, parent)
        self.setDefaultTextColor(colors['comment'])
    
    def toData(self):
        data = super(Comment, self).toData()
        data['type'] = 'comment'
        return data

def isTextItem(item):
    return isinstance(item, textItem)
    
def isComment(item):
    return isinstance(item, Comment)
    