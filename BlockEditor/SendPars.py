# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SendPars.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(440, 413)
        self.gridLayoutWidget = QtWidgets.QWidget(Dialog)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(20, 60, 391, 271))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.pbSend = QtWidgets.QPushButton(Dialog)
        self.pbSend.setGeometry(QtCore.QRect(160, 350, 83, 24))
        self.pbSend.setObjectName("pbSend")
        self.spVars = QtWidgets.QSpinBox(Dialog)
        self.spVars.setGeometry(QtCore.QRect(220, 11, 121, 31))
        self.spVars.setMinimum(1)
        self.spVars.setMaximum(12)
        self.spVars.setObjectName("spVars")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(100, 20, 91, 16))
        self.label.setObjectName("label")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.pbSend.setText(_translate("Dialog", "SEND"))
        self.label.setText(_translate("Dialog", "Variables"))

