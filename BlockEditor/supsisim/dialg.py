#!/usr/bin/python
# aim for python 2/3 compatibility
from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

from  Qt import QtGui, QtWidgets, QtCore # see https://github.com/mottosso/Qt.py
import sys, os, re
from collections import OrderedDict

#if sys.version_info>(3,0):
#    import sip
#    sip.setapi('QString', 1)
#
from supsisim.const import path,respath
import libraries

class editPinsDialog(QtWidgets.QDialog):
    def __init__(self,inps, outps, title='Edit pins', size=(600, 300), parent=None): 
        super(editPinsDialog, self).__init__(parent)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(QtWidgets.QLabel('Inputs'))
        self.text_input = QtWidgets.QWidget()
        self.input_layout = QtWidgets.QVBoxLayout()
        self.text_input.setLayout(self.input_layout)
        
        inputLabels = QtWidgets.QWidget()
        inputLabels_layout = QtWidgets.QHBoxLayout()        
        inputLabels_layout.addWidget(QtWidgets.QLabel('Name'))
        inputLabels_layout.addWidget(QtWidgets.QLabel('   X'))
        inputLabels_layout.addWidget(QtWidgets.QLabel('       Y'))
        inputLabels_layout.addWidget(QtWidgets.QLabel('     Hide label'))
        inputLabels_layout.addWidget(QtWidgets.QLabel())
        inputLabels.setLayout(inputLabels_layout)
        self.input_layout.addWidget(inputLabels)        
        
        self.layout.addWidget(self.text_input)
        
        
        self.addInput = QtWidgets.QPushButton('Add input')
        self.addInput.clicked.connect(self.addInputFunc)
        self.layout.addWidget(self.addInput)        
        
        self.layout.addWidget(QtWidgets.QLabel('Outputs'))
        self.text_output = QtWidgets.QWidget()
        self.output_layout = QtWidgets.QVBoxLayout()
        self.text_output.setLayout(self.output_layout)
        
        ouputLabels = QtWidgets.QWidget()
        ouputLabels_layout = QtWidgets.QHBoxLayout()        
        ouputLabels_layout.addWidget(QtWidgets.QLabel('Name'))
        ouputLabels_layout.addWidget(QtWidgets.QLabel('   X'))
        ouputLabels_layout.addWidget(QtWidgets.QLabel('       Y'))
        ouputLabels_layout.addWidget(QtWidgets.QLabel('     Hide label'))
        ouputLabels_layout.addWidget(QtWidgets.QLabel())
        ouputLabels.setLayout(ouputLabels_layout)
        self.output_layout.addWidget(ouputLabels)           
        
        self.layout.addWidget(self.text_output)
        
        
        self.addOutput = QtWidgets.QPushButton('Add output')
        self.addOutput.clicked.connect(self.addOutputFunc)  
        self.layout.addWidget(self.addOutput)          
        
        
        
        
        
        # Cancel and OK buttons
        buttons = QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Cancel
        self.bbox = QtWidgets.QDialogButtonBox(buttons)
        self.bbox.accepted.connect(self.accept)
        self.bbox.rejected.connect(self.reject)
        self.layout.addWidget(self.bbox)
        
        # set window title and window size
        self.setWindowTitle(title)
        self.resize(size[0], size[1])   
        
        self.inputInstances = []
        self.outputInstances = []
        
        self.inputCounter = 0
        self.outputCounter = 0
        
        if isinstance(inps,int):
            for _ in range(inps):
                self.addInputFunc(hide=True)
        else:
            for inp in inps:
                if len(inp) == 4:
                    self.addInputFunc(inp[0],inp[1],inp[2],inp[3])
                else:
                    self.addInputFunc(inp[0],inp[1],inp[2])
        if isinstance(outps,int):
            for _ in range(outps):
                self.addInputFunc(hide=True)
        else:
            for outp in outps:
                if len(outp) == 4:
                    self.addOutputFunc(outp[0],outp[1],outp[2],outp[3])
                else:
                    self.addOutputFunc(outp[0],outp[1],outp[2])
                
  
        
    def addInputFunc(self,name=None,x=None,y=None,hide=False):
        if not name:
            name = 'i_pin' + str(self.inputCounter)
        if x is None:
            x = '-40'
        if y is None:
            y = self.inputCounter*20
        inputInstance = QtWidgets.QWidget()
        inputInstance_layout = QtWidgets.QHBoxLayout()
        
        
        text_name = QtWidgets.QLineEdit(name)
        font = QtGui.QFont()
        font.setFamily('Lucida')
        font.setFixedPitch(True)
        font.setPointSize(12)
        text_name.setFont(font)
        inputInstance_layout.addWidget(text_name)
        
        text_x = QtWidgets.QLineEdit(str(x))
        font = QtGui.QFont()
        font.setFamily('Lucida')
        font.setFixedPitch(True)
        font.setPointSize(12)
        text_x.setFont(font)
        inputInstance_layout.addWidget(text_x)
        
        text_y = QtWidgets.QLineEdit(str(y))
        font = QtGui.QFont()
        font.setFamily('Lucida')
        font.setFixedPitch(True)
        font.setPointSize(12)
        text_y.setFont(font)
        inputInstance_layout.addWidget(text_y)
        
        inputHide = QtWidgets.QCheckBox()
        inputHide.setChecked(hide)
        inputInstance_layout.addWidget(inputHide)
        
        
        removeButton = QtWidgets.QPushButton('Remove')
        
        def getFunction(inputInstance,element):
            def removeInp():
                self.input_layout.removeWidget(inputInstance)
                self.inputInstances.remove(element)
                self.inputCounter -= 1
            return removeInp
        removeButton.clicked.connect(getFunction(inputInstance,(text_name,text_x,text_y,inputHide)))
        inputInstance_layout.addWidget(removeButton)
        
        
        
        inputInstance.setLayout(inputInstance_layout)
        self.input_layout.addWidget(inputInstance)
        self.inputInstances.append((text_name,text_x,text_y,inputHide))
        
        
        self.inputCounter += 1
    
    def addOutputFunc(self,name=None,x=None,y=None,hide=False):
        if not name:
            name = 'o_pin' + str(self.outputCounter)
        if x is None:
            x = '40'
        if y is None:
            y = self.outputCounter*20
            
        outputInstance = QtWidgets.QWidget()
        outputInstance_layout = QtWidgets.QHBoxLayout()
        
        
        text_name = QtWidgets.QLineEdit(name)
        font = QtGui.QFont()
        font.setFamily('Lucida')
        font.setFixedPitch(True)
        font.setPointSize(12)
        text_name.setFont(font)
        outputInstance_layout.addWidget(text_name)
        
        text_x = QtWidgets.QLineEdit(str(x))
        font = QtGui.QFont()
        font.setFamily('Lucida')
        font.setFixedPitch(True)
        font.setPointSize(12)
        text_x.setFont(font)
        outputInstance_layout.addWidget(text_x)
        
        text_y = QtWidgets.QLineEdit(str(y))
        font = QtGui.QFont()
        font.setFamily('Lucida')
        font.setFixedPitch(True)
        font.setPointSize(12)
        text_y.setFont(font)
        outputInstance_layout.addWidget(text_y)
        
                
        
        outputHide = QtWidgets.QCheckBox()
        outputHide.setChecked(hide)
        outputInstance_layout.addWidget(outputHide)
        
        
        removeButton = QtWidgets.QPushButton('Remove')
        
        def getFunction(inputInstance,element):
            def removeInp():
                self.output_layout.removeWidget(outputInstance)
                self.outputInstances.remove(element)
                self.outputCounter -= 1
            return removeInp
        removeButton.clicked.connect(getFunction(outputInstance,(text_name,text_x,text_y,outputHide)))
        outputInstance_layout.addWidget(removeButton)
        
        
        outputInstance.setLayout(outputInstance_layout)
        self.output_layout.addWidget(outputInstance)
        self.outputInstances.append((text_name,text_x,text_y,outputHide))
        
        self.outputCounter += 1
    
    
    def selectIcon(self):
        self.filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open',respath + '/blocks/', filter='*.svg')
    
    def getRet(self):
        if self.exec_():
            inputList = []
            outputList = []
            
            for inp in self.inputInstances:
                name = inp[0].text()
                x = int(inp[1].text())
                y = int(inp[2].text())
                if inp[3].isChecked():
                    inputList.append((name,x,y,True))
                else:
                    inputList.append((name,x,y))
                
            for outp in self.outputInstances:
                name = outp[0].text()
                x = int(outp[1].text())
                y = int(outp[2].text())
                if outp[3].isChecked():
                    outputList.append((name,x,y,True))
                else:
                    outputList.append((name,x,y))
                
                
            return (inputList,outputList, [])         
        else:
            return False






#class propertiesDialog(QtWidgets.QDialog):
#    def __init__(self, properties, addButton=True):
#        super(propertiesDialog, self).__init__(None)
#        self.properties = properties
#        self.grid = QtWidgets.QGridLayout()
#        self.values = dict()
#        self.n = 0
#        for p in properties.keys():
#            if p != "name":
#                Lab = QtWidgets.QLabel(p)
#                Val = QtWidgets.QLineEdit(str(properties[p]))
#                self.values[p] = Val
#                self.grid.addWidget(Lab,self.n,0)
#                self.grid.addWidget(Val,self.n,1)
#                self.n += 1
#        
#        if addButton:
#            self.key_field = QtWidgets.QLineEdit('key')
#            self.addProperty = QtWidgets.QPushButton('Add property')
#            self.addProperty.clicked.connect(self.addPropertyAction)  
#            self.grid.addWidget(self.key_field,99,0)
#            self.grid.addWidget(self.addProperty,99,1)
#        
#        
#        self.pbOK = QtWidgets.QPushButton('OK')
#        self.pbCANCEL = QtWidgets.QPushButton('CANCEL')
#        self.grid.addWidget(self.pbOK,100,0)
#        self.grid.addWidget(self.pbCANCEL,100,1)
#        self.pbOK.clicked.connect(self.accept)
#        self.pbCANCEL.clicked.connect(self.reject)
#        self.setLayout(self.grid)
#
#
#    def addPropertyAction(self):
#        key = self.key_field.text()
#        Lab = QtWidgets.QLabel(key)
#        Val = QtWidgets.QLineEdit('0')
#        self.values[key] = Val
#        self.grid.addWidget(Lab,self.n,0)
#        self.grid.addWidget(Val,self.n,1)
#        self.n += 1
#
#    def getRet(self):
#        if self.exec_():
#            if 'name' in self.properties.keys():
#                newProperties = dict(name=self.properties['name'])
#            else:
#                newProperties = dict()
#            for key in self.values.keys():
#                newProperties[key] = eval(self.values[key].text())
#            return newProperties
#        else:
#            False

class LibraryChoice_Dialog(QtWidgets.QMessageBox):
    def __init__(self,parent=None):
        super(LibraryChoice_Dialog,self).__init__(parent)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setWindowTitle('Library')
        self.setText("What library would you like to use")
        self.addButton('List view',self.YesRole)
        self.addButton('Symbol view',self.NoRole)
        
class overWriteNetlist(QtWidgets.QMessageBox):
    def __init__(self,parent=None):
        super(overWriteNetlist,self).__init__(parent)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setWindowTitle('Overwrite')
        self.setText("Would you like to overwrite the current file")
        self.addButton('Yes',self.YesRole)
        self.addButton('No',self.NoRole)
        
class error(QtWidgets.QMessageBox):
    def __init__(self,errorMessage,parent=None, warn=False):
        super(error,self).__init__(parent)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        if warn: 
            self.setWindowTitle('Warning')
            self.setText("Warning: " + errorMessage)
        else:
            self.setWindowTitle('Error')
            self.setText("Error: " + errorMessage)
        self.exec_()

class IO_Dialog(QtWidgets.QDialog):
    def __init__(self,parent=None):
        super(IO_Dialog, self).__init__(parent)
        layout = QtWidgets.QGridLayout()
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.resize(380, 180)
        self.spbInput = QtWidgets.QSpinBox()
        self.spbOutput = QtWidgets.QSpinBox()
        self.spbInput.setValue(1)
        self.spbOutput.setValue(1)

        label2 = QtWidgets.QLabel('Number of inputs:')
        label3 = QtWidgets.QLabel('Number of outputs')
        self.pbOK = QtWidgets.QPushButton('OK')
        self.pbCANCEL = QtWidgets.QPushButton('CANCEL')
        layout.addWidget(self.spbInput,0,1)
        layout.addWidget(self.spbOutput,1,1)
        layout.addWidget(label2,0,0)
        layout.addWidget(label3,1,0)
        layout.addWidget(self.pbOK,2,0)
        layout.addWidget(self.pbCANCEL,2,1)
        self.setLayout(layout)
        self.pbOK.clicked.connect(self.accept)
        self.pbCANCEL.clicked.connect(self.reject)

class propertiesDialog(QtWidgets.QDialog):
    '''general dialog
    takes dict dd: keys are the fieldnames (underscore replaced with space), 
    values:
        stringtype                  -> line_edit
        (default, [list of options])-> combo box
        int                         -> spinbox
            alternatively use tuple:
            (int, dict(prefix='', suffix='', min=None, max=None))
            '''

    def __init__(self, parent=None, dd=dict(), properties=None, title=None, addButton=True):
        super(propertiesDialog, self).__init__(parent)
        self.layout = QtWidgets.QGridLayout()
        self.keyix = OrderedDict()
        self.propix = OrderedDict()
        self.w = []
        self.n = 0
#        addButton = not properties is None
        self.dd = dd
        self.addrows(dd, properties)

        if addButton:
            self.key_field = QtWidgets.QLineEdit()
            self.key_field.setPlaceholderText('property name')
            self.addProperty = QtWidgets.QPushButton('Add property')
            self.addProperty.clicked.connect(self.addPropertyAction)  
            self.layout.addWidget(self.key_field,99,0)
            self.layout.addWidget(self.addProperty,99,1)
        
        
        self.pbOK = QtWidgets.QPushButton('OK')
        self.pbCANCEL = QtWidgets.QPushButton('Cancel')
        self.layout.addWidget(self.pbOK,100,0)
        self.layout.addWidget(self.pbCANCEL,100,1)
        self.pbOK.clicked.connect(self.accept)
        self.pbCANCEL.clicked.connect(self.reject)
        self.setLayout(self.layout)
        if title:
            self.setWindowTitle(title)

    def addrows(self, dd, properties):
        for ddd, propflag in [(dd, False), (properties, True)]:
            if ddd is None:
                return
            for k, v  in ddd.items():
                w = None
                if isinstance(v, basestring) or v is None:
                    w = QtWidgets.QLineEdit()
                    if v is None:
                        w.setText('None')
                    elif v:
                        w.setText(v)
                    else:
                        w.setPlaceholderText(k)
                elif isinstance(v, int):
                    w = QtWidgets.QSpinBox()
                    w.setValue(v)
                elif isinstance(v, float):
                    w = QtWidgets.QLineEdit()
                    w.setText(str(v))
                elif isinstance(v, (list, tuple)) and len(v) == 2:
                    default, options = v
                    if isinstance(default, int):
                        w = QtWidgets.QSpinBox()
                        w.setValue(default)
                        for kk, func in [('prefix',  w.setPrefix),
                                         ('suffix' , w.setSuffix),
                                         ('min',     w.setMinimum),
                                         ('max',     w.setMaximum)]:
                             if kk in options:
                                 func(options[kk])
                    elif isinstance(default, basestring):
                        w = QtWidgets.QComboBox()
                        for elem in options:
                            w.addItem(elem)
                        if default in options:
                            ix = options.index(default)
                            w.setCurrentIndex(ix)
                if w:
                    txt = k.replace('_', ' ')
                    if propflag:
                        self.propix[k] = len(self.w)
                    else:
                        self.keyix[k] = len(self.w)
                    self.w.append(w)
                    self.layout.addWidget(QtWidgets.QLabel(txt), self.n, 0)
                    self.layout.addWidget(w, self.n, 1)
                    self.n += 1

    def addPropertyAction(self):
        key = self.key_field.text()
        if key: # make sure no empty key
            w = QtWidgets.QLineEdit('0')
            self.layout.addWidget(QtWidgets.QLabel(key), self.n, 0)
            self.propix[key] = len(self.w)
            self.w.append(w)
            self.layout.addWidget(w, self.n, 1)
            self.n += 1

    def getRet(self):
        if self.exec_():
            dd = dict()
            for k, ix in self.keyix.items():
                if isinstance(self.w[ix], QtWidgets.QLineEdit):
                    v = self.w[ix].text()
                    if v == 'None':
                        dd[k] = None
                    else:
                        try:
                            dd[k] = eval(v)
                        except NameError:
                            dd[k] = v                    
                elif isinstance(self.w[ix], QtWidgets.QComboBox):
                    v = self.w[ix].currentText()
                    if isinstance(self.dd[k], (list, tuple)) and len(self.dd[k]) == 2:
                        dd[k] = (v, self.dd[k][1])
                    else:
                        dd[k] = v
                elif isinstance(self.w[ix], QtWidgets.QSpinBox):
                    dd[k] = self.w[ix].value()
                elif isinstance(self.w[ix], QtWidgets.QDoubleSpinBox):
                    dd[k] = self.w[ix].value()
            properties = dict()
            for k, ix in self.propix.items():
                val = self.w[ix].text()
                try:
                    v = eval(val)
                except NameError:
                    v = val
                if isinstance(self.dd[k], (list, tuple)) and len(self.dd[k]) == 2:
                    properties[k] = (v, self.dd[k][1])
                else:
                    properties[k] = v
#            dd['properties'] = properties 
            dd.update(properties)
            return dd

   
        
class BlockName_Dialog(QtWidgets.QDialog):
    def __init__(self,parent=None):
        super(BlockName_Dialog, self).__init__(parent)
        layout = QtWidgets.QGridLayout()
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.resize(380, 100)
        self.name = QtWidgets.QLineEdit()

        label1 = QtWidgets.QLabel('Block ID:')
        self.pbOK = QtWidgets.QPushButton('OK')
        self.pbCANCEL = QtWidgets.QPushButton('CANCEL')
        layout.addWidget(label1,0,0)
        layout.addWidget(self.name,0,1)
        layout.addWidget(self.pbOK,2,0)
        layout.addWidget(self.pbCANCEL,2,1)
        self.setLayout(layout)
        self.pbOK.clicked.connect(self.accept)
        self.pbCANCEL.clicked.connect(self.reject)

class RTgenDlg(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(RTgenDlg, self).__init__(None)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.resize(380, 100)
        lab1 = QtWidgets.QLabel('Template Makefile')
        self.template = QtWidgets.QLineEdit('')
        btn_template = QtWidgets.QPushButton('BROWSE...')
        lab2 = QtWidgets.QLabel('Additional Objs')
        self.addObjs = QtWidgets.QLineEdit('')
        btn_addObjs = QtWidgets.QPushButton('BROWSE...')
        lab3 = QtWidgets.QLabel('Sampling Time')
        self.Ts = QtWidgets.QLineEdit('')
        lab4 = QtWidgets.QLabel('Parameter script')
        self.parscript = QtWidgets.QLineEdit('')
        btn_script = QtWidgets.QPushButton('BROWSE...')
        lab5 = QtWidgets.QLabel('Final Time')
        self.Tf = QtWidgets.QLineEdit('')
        pbOK = QtWidgets.QPushButton('OK')
        pbCANCEL = QtWidgets.QPushButton('CANCEL')
        grid = QtWidgets.QGridLayout()
        grid.addWidget(lab1,0,0)
        grid.addWidget(self.template,0,1)
        grid.addWidget(btn_template,0,2)
        grid.addWidget(lab2,1,0)
        grid.addWidget(self.addObjs,1,1)
        grid.addWidget(btn_addObjs,1,2)
        grid.addWidget(lab3,2,0)
        grid.addWidget(self.Ts,2,1)
        grid.addWidget(lab4,3,0)
        grid.addWidget(self.parscript,3,1)
        grid.addWidget(btn_script,3,2)
        grid.addWidget(lab5,4,0)
        grid.addWidget(self.Tf,4,1)
        grid.addWidget(pbOK,6,0)
        grid.addWidget(pbCANCEL,6,1)
        pbOK.clicked.connect(self.accept)
        pbCANCEL.clicked.connect(self.reject)
        btn_template.clicked.connect(self.getTemplate)
        btn_addObjs.clicked.connect(self.getObjs)
        btn_script.clicked.connect(self.getScript)
        self.setLayout(grid)

    def getTemplate(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(self,'Open Template Makefile',
                                                  os.path.join(path,'CodeGen','templates'), 'Template (*.tmf)')
        if isinstance(fname, tuple): # PqQt5 returns a tuple (filename, filter), PyQt4 apparently not
            fname = fname[0]
        if len(fname) != 0:
            head, templ = os.path.split(fname)
            self.template.setText(templ)

    def getObjs(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(self,'Additional libraries',
                                                  '.','Dynamic libraries (*.so)')
        if isinstance(fname, tuple): # PqQt5 returns a tuple (filename, filter)
            fname = fname[0]
        if len(fname) != 0:
            head, libname = os.path.split(fname)
            self.addObjs.setText(libname)

    def getScript(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(self,'Open Python script',
                                                  '.', 'Python file (*.py)')
        if isinstance(fname, tuple): # PqQt5 returns a tuple (filename, filter)
            fname = fname[0]
        if len(fname) != 0:
            head, script = os.path.split(fname)
            self.parscript.setText(script)

class txtDialog(QtWidgets.QDialog):
    def __init__(self, title='TextEditor', size=(400, 300), parent=None): # pins is a listof tuples: (name, type, x, y)
        '''display text, and edit the contents'''
        super(txtDialog, self).__init__(parent)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        # edit widget
        self.text_edit = QtWidgets.QTextEdit(parent)
        font = QtGui.QFont()
        font.setFamily('Lucida')
        font.setFixedPitch(True)
        font.setPointSize(12)
        self.text_edit.setFont(font)
        self.layout.addWidget(self.text_edit)
        
        # Cancel and OK buttons
        buttons = QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Cancel
        self.bbox = QtWidgets.QDialogButtonBox(buttons)
        self.bbox.accepted.connect(self.accept)
        self.bbox.rejected.connect(self.reject)
        self.layout.addWidget(self.bbox)

        # set window title and window size
        self.setWindowTitle(title)
        self.resize(size[0], size[1])
        
    def editTxt(self, txt):
        '''display txt and return edited txt'''
        self.text_edit.setText(txt)
        if self.exec_(): #Ok
            return self.text_edit.toPlainText()
        else: # Cancel   
            return False 
   
    def editList(self, llist, header=''):
        '''display the list in tabular format and return edited list'''
        col_w = [] # widths
        col_t = [] # types

        if header:
            for c in ('#'+header).split():
                col_w.append(len(c))

        for line in llist:
            for ix, c in enumerate(line):
                if ix >= len(col_t):
                    col_w.append(1)
                    col_t.append(type(c))
                
                col_w[ix] = max(len('{}'.format(c)), col_w[ix])
                if not isinstance(col_t[ix], float):
                    col_t[ix] = c
        t = []
        for w, tp in zip(col_w, col_t):
            if isinstance(tp, (int, float)):
                t.append('{: '+str(w)+'}')
            else:
                t.append('{:^'+str(w)+'}')
                
        t[-1] = '{}'
        fmt = ' '.join(t)+'\n'
        fmt1 = fmt.replace(': ', ':')
        fmt0 = fmt.replace(': ', ':^')
        
        txt = fmt0.format(*('#'+header).split()) if header else ''
        for line in llist:
            try:
                txt += fmt.format(*line)
            except ValueError:
                txt += fmt1.format(*line)
                
        txt = self.editTxt(txt)
        if txt:
            lres = []
            for line in txt.splitlines():
                if line.strip() and not line.strip().startswith('#'):
                    try:
                        cres = [type(col_t[ix])(c) for ix, c in enumerate(line.split())]
                        lres.append(cres)
                    except:
                        print('ignored:', line)
            return lres
        else:
            return txt

class textLineDialog(QtWidgets.QDialog):
    def __init__(self, label, title='Add Label',content="", size=(300, 100), parent=None):
        super(textLineDialog, self).__init__(parent)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        
        self.layout.addWidget(QtWidgets.QLabel(label))
        # edit widget
        self.text_edit = QtWidgets.QLineEdit(content,parent)
        font = QtGui.QFont()
        font.setFamily('Lucida')
        font.setFixedPitch(True)
        font.setPointSize(12)
        self.text_edit.setFont(font)
        self.layout.addWidget(self.text_edit)
        
        # Cancel and OK buttons
        buttons = QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Cancel
        self.bbox = QtWidgets.QDialogButtonBox(buttons)
        self.bbox.accepted.connect(self.accept)
        self.bbox.rejected.connect(self.reject)
        self.layout.addWidget(self.bbox)

        # set window title and window size
        self.setWindowTitle(title)
        self.resize(size[0], size[1])
        
    def getLabel(self):
        if self.exec_(): #Ok
            return self.text_edit.text()
        else: # Cancel   
            return False 

class viewConfigDialog(QtWidgets.QDialog):
    def __init__(self, title='View settings', size=(400, 300), parent=None): 
        super(viewConfigDialog, self).__init__(parent)
        self.layout = self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        self.viewWidgets = []
        self.n = 1

        import supsisim.const
        reload(supsisim.const)
        from supsisim.const import viewTypes     
        
            
        self.layout.addWidget(QtWidgets.QLabel("viewtype:"),0,0)
        self.layout.addWidget(QtWidgets.QLabel("editor command:"),0,1)
        self.layout.addWidget(QtWidgets.QLabel("extension:"),0,2)
        # edit widget
        for viewtype, (viewEditor, extension) in viewTypes.items():
            
            view_w = QtWidgets.QLabel(viewtype )
            self.layout.addWidget(view_w,self.n,0)
    
            editor_w = QtWidgets.QLineEdit(viewEditor)
            font = QtGui.QFont()
            font.setFamily('Lucida')
            font.setFixedPitch(True)
            font.setPointSize(12)
            editor_w.setFont(font)
            self.layout.addWidget(editor_w,self.n,1)
            
            extension_w = QtWidgets.QLineEdit(extension)
            font = QtGui.QFont()
            font.setFamily('Lucida')
            font.setFixedPitch(True)
            font.setPointSize(12)
            extension_w.setFont(font)
            self.layout.addWidget(extension_w,self.n,2)
            self.n += 1
            self.viewWidgets.append(dict(type=viewtype,editor=viewEditor,extension=extension))
        
        
        # Cancel and OK buttons
        buttons = QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Cancel
        self.bbox = QtWidgets.QDialogButtonBox(buttons)
        self.bbox.accepted.connect(self.accept)
        self.bbox.rejected.connect(self.reject)
        self.layout.addWidget(self.bbox, self.n,2)

        # set window title and window size
        self.setWindowTitle(title)
        self.resize(size[0], size[1])   
    
    
    
    def getRet(self):
        if self.exec_():
            ret = []
            for i,value in enumerate(self.viewWidgets):
                ret.append(dict(type=value['type'],editor=value['editor'].text(),extension=value['extension'].text()))
            return ret         
        else:
            return False

class addViewDialog(QtWidgets.QDialog):
    def __init__(self, libname, blockname, title='Add view', size=(400, 300), parent=None): 
        super(addViewDialog, self).__init__(parent)
        
        self.setWindowTitle(title)
        self.resize(size[0], size[1]) 
        
        self.grid = QtWidgets.QGridLayout()

        self.string = os.path.join(os.path.basename(libraries.libroot), libraries.libprefix+libname, blockname)
    
        self.textSource = QtWidgets.QLineEdit(self.string)
        
        self.selectView = QtWidgets.QComboBox()
        self.selectView.currentIndexChanged.connect(self.selectViewChanged)
        

        import supsisim.const
        reload(supsisim.const)
        from supsisim.const import viewTypes         
        
        for viewtype, (ed, ext) in viewTypes.items():
            self.selectView.addItem(viewtype)
    
        self.grid.addWidget(self.selectView,0,0)
        self.grid.addWidget(self.textSource,0,1)
    
        self.pbOK = QtWidgets.QPushButton('OK')
        self.pbCANCEL = QtWidgets.QPushButton('CANCEL')
        self.grid.addWidget(self.pbOK,1,0)
        self.grid.addWidget(self.pbCANCEL,1,1)
        self.pbOK.clicked.connect(self.accept)
        self.pbCANCEL.clicked.connect(self.reject)
        self.setLayout(self.grid)
        
    def selectViewChanged(self,i):
        from supsisim.const import viewTypes     
        viewType = self.selectView.currentText()
        ed, extension = viewTypes[viewType]
        self.textSource.setText(self.string + extension)

    def getRet(self):
        if self.exec_():
            return (self.selectView.currentText(),self.textSource.text())
        else:
            return False

class createBlockDialog(QtWidgets.QDialog):
    def __init__(self, title='Create block', size=(400, 300), parent=None): 
        super(createBlockDialog, self).__init__(parent)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        # edit widget
        self.layout.addWidget(QtWidgets.QLabel('Name'))

        self.text_name = QtWidgets.QLineEdit(parent)
        font = QtGui.QFont()
        font.setFamily('Lucida')
        font.setFixedPitch(True)
        font.setPointSize(12)
        self.text_name.setFont(font)
        self.layout.addWidget(self.text_name)
        
        self.layout.addWidget(QtWidgets.QLabel('Icon'))
        self.text_icon = QtWidgets.QWidget()
        self.icon_layout = QtWidgets.QHBoxLayout()
#        self.icon_createBtn = QtWidgets.QPushButton('Create Icon')    
        self.icon_selectIcon = QtWidgets.QPushButton('Select Icon')
        self.icon_selectIcon.clicked.connect(self.selectIcon)        
#        self.icon_layout.addWidget(self.icon_createBtn)
        self.icon_layout.addWidget(self.icon_selectIcon)
        self.text_icon.setLayout(self.icon_layout)
        self.layout.addWidget(self.text_icon)        
        
        
        
        self.layout.addWidget(QtWidgets.QLabel('Inputs'))
        self.text_input = QtWidgets.QWidget()
        self.input_layout = QtWidgets.QVBoxLayout()
        self.text_input.setLayout(self.input_layout)
        

        inputLabels = QtWidgets.QWidget()
        inputLabels_layout = QtWidgets.QHBoxLayout()        
        inputLabels_layout.addWidget(QtWidgets.QLabel('Name'))
        inputLabels_layout.addWidget(QtWidgets.QLabel('      X'))
        inputLabels_layout.addWidget(QtWidgets.QLabel('           Y'))
        inputLabels_layout.addWidget(QtWidgets.QLabel('         Hide label'))
        inputLabels.setLayout(inputLabels_layout)
        self.input_layout.addWidget(inputLabels)        
        
        self.layout.addWidget(self.text_input)
        
        
        self.addInput = QtWidgets.QPushButton('Add input')
        self.addInput.clicked.connect(self.addInputFunc)
        self.layout.addWidget(self.addInput)        
        
        self.layout.addWidget(QtWidgets.QLabel('Outputs'))
        self.text_output = QtWidgets.QWidget()
        self.output_layout = QtWidgets.QVBoxLayout()
        self.text_output.setLayout(self.output_layout)
        
        ouputLabels = QtWidgets.QWidget()
        ouputLabels_layout = QtWidgets.QHBoxLayout()        
        ouputLabels_layout.addWidget(QtWidgets.QLabel('Name'))
        ouputLabels_layout.addWidget(QtWidgets.QLabel('      X'))
        ouputLabels_layout.addWidget(QtWidgets.QLabel('           Y'))
        ouputLabels_layout.addWidget(QtWidgets.QLabel('         Hide label'))
        ouputLabels.setLayout(ouputLabels_layout)
        self.output_layout.addWidget(ouputLabels)           
        
        self.layout.addWidget(self.text_output)
        
        
        self.addOutput = QtWidgets.QPushButton('Add output')
        self.addOutput.clicked.connect(self.addOutputFunc)  
        self.layout.addWidget(self.addOutput)          
        
        
        
        
        
        
        
        self.layout.addWidget(QtWidgets.QLabel('Parameters'))
        self.warningLabel = QtWidgets.QLabel("Don't forget to add a parameter function to the text view")
        myFont=QtGui.QFont()
        myFont.setItalic(True)
        self.warningLabel.setFont(myFont)     
        self.layout.addWidget(self.warningLabel)
        self.text_parameters = QtWidgets.QWidget()
        
        self.gridPar = QtWidgets.QGridLayout()
        self.valuesPar = dict()
        self.nPar = 0
        
        self.key_fieldPar = QtWidgets.QLineEdit('key')
        self.addParam = QtWidgets.QPushButton('Add parameter')
        self.addParam.clicked.connect(self.addParamAction)  
        self.gridPar.addWidget(self.key_fieldPar,99,0)
        self.gridPar.addWidget(self.addParam,99,1)
        
        
        
        self.text_parameters.setLayout(self.gridPar)
        self.layout.addWidget(self.text_parameters)        
        
        
        #        
#           
        
        self.layout.addWidget(QtWidgets.QLabel('Properties'))
        self.text_properties = QtWidgets.QWidget()
        
        self.grid = QtWidgets.QGridLayout()
        self.values = dict()
        self.n = 0
        
        self.key_field = QtWidgets.QLineEdit('key')
        self.addProperty = QtWidgets.QPushButton('Add property')
        self.addProperty.clicked.connect(self.addPropertyAction)  
        self.grid.addWidget(self.key_field,99,0)
        self.grid.addWidget(self.addProperty,99,1)
        
        
        
        self.text_properties.setLayout(self.grid)
        self.layout.addWidget(self.text_properties)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        # Cancel and OK buttons
        buttons = QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Cancel
        self.bbox = QtWidgets.QDialogButtonBox(buttons)
        self.bbox.accepted.connect(self.accept)
        self.bbox.rejected.connect(self.reject)
        self.layout.addWidget(self.bbox)
        
        # set window title and window size
        self.setWindowTitle(title)
        self.resize(size[0], size[1])   
        
        self.inputInstances = []
        self.outputInstances = []
        
        self.inputCounter = 0
        self.outputCounter = 0
        self.filename = (0,0)
    
    def addParamAction(self):
        key = self.key_fieldPar.text()
        Lab = QtWidgets.QLabel(key)
        Val = QtWidgets.QLineEdit('0')
        self.valuesPar[key] = Val
        self.gridPar.addWidget(Lab,self.nPar,0)
        self.gridPar.addWidget(Val,self.nPar,1)
        self.nPar += 1  
        
    def addPropertyAction(self):
        key = self.key_field.text()
        Lab = QtWidgets.QLabel(key)
        Val = QtWidgets.QLineEdit('0')
        self.values[key] = Val
        self.grid.addWidget(Lab,self.n,0)
        self.grid.addWidget(Val,self.n,1)
        self.n += 1    
        
    def addInputFunc(self):
        inputInstance = QtWidgets.QWidget()
        inputInstance_layout = QtWidgets.QHBoxLayout()
        
        
        text_name = QtWidgets.QLineEdit('i_pin' + str(self.inputCounter))
        font = QtGui.QFont()
        font.setFamily('Lucida')
        font.setFixedPitch(True)
        font.setPointSize(12)
        text_name.setFont(font)
        inputInstance_layout.addWidget(text_name)
        
        text_x = QtWidgets.QLineEdit('-40')
        font = QtGui.QFont()
        font.setFamily('Lucida')
        font.setFixedPitch(True)
        font.setPointSize(12)
        text_x.setFont(font)
        inputInstance_layout.addWidget(text_x)
        
        text_y = QtWidgets.QLineEdit(str(self.inputCounter*20))
        font = QtGui.QFont()
        font.setFamily('Lucida')
        font.setFixedPitch(True)
        font.setPointSize(12)
        text_y.setFont(font)
        inputInstance_layout.addWidget(text_y)
        
        inputHide = QtWidgets.QCheckBox()
        inputInstance_layout.addWidget(inputHide)
        
        
        
        inputInstance.setLayout(inputInstance_layout)
        self.input_layout.addWidget(inputInstance)
        self.inputInstances.append((text_name,text_x,text_y,inputHide))
        
        
        self.inputCounter += 1
    
    def addOutputFunc(self):
        outputInstance = QtWidgets.QWidget()
        outputInstance_layout = QtWidgets.QHBoxLayout()
        
        
        text_name = QtWidgets.QLineEdit('o_pin' + str(self.outputCounter))
        font = QtGui.QFont()
        font.setFamily('Lucida')
        font.setFixedPitch(True)
        font.setPointSize(12)
        text_name.setFont(font)
        outputInstance_layout.addWidget(text_name)
        
        text_x = QtWidgets.QLineEdit('40')
        font = QtGui.QFont()
        font.setFamily('Lucida')
        font.setFixedPitch(True)
        font.setPointSize(12)
        text_x.setFont(font)
        outputInstance_layout.addWidget(text_x)
        
        text_y = QtWidgets.QLineEdit(str(self.outputCounter*20))
        font = QtGui.QFont()
        font.setFamily('Lucida')
        font.setFixedPitch(True)
        font.setPointSize(12)
        text_y.setFont(font)
        outputInstance_layout.addWidget(text_y)
        
        
        outputHide = QtWidgets.QCheckBox()
        outputInstance_layout.addWidget(outputHide)
        
        
        
        outputInstance.setLayout(outputInstance_layout)
        self.output_layout.addWidget(outputInstance)
        self.outputInstances.append((text_name,text_x,text_y,outputHide))
        
        self.outputCounter += 1
    
    
    def selectIcon(self):
        self.filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open',respath + '/blocks/', filter='*.svg')
    
    def getRet(self):
        if self.exec_():
            ret = dict()
            if not self.text_name.text():
                error('Name required')
                return False
            if not re.match(r'[a-z_]\w*$', self.text_name.text(), re.I):
                error(self.text_name.text() + ' is not valid variable name')
                return False
            if not self.filename[0]:
                error('no icon set', warn=True)
                ret['icon']= None 
            else:
                ret['icon'] = QtCore.QFileInfo(self.filename[0]).baseName()
               
            ret['name'] = self.text_name.text()
            ret['input'] = []
            ret['output'] = []
            
            for inp in self.inputInstances:
                name = inp[0].text()
                x = int(inp[1].text())
                y = int(inp[2].text())
                if inp[3].isChecked():
                    ret['input'].append((name,x,y,True))
                else:
                    ret['input'].append((name,x,y))
                
            for outp in self.outputInstances:
                name = outp[0].text()
                x = int(outp[1].text())
                y = int(outp[2].text())
                if outp[3].isChecked():
                    ret['output'].append((name,x,y,True))
                else:
                    ret['output'].append((name,x,y))
                
            ret['inout'] = []
            
            newProperties = dict()
            for key in self.values.keys():
                newProperties[key] = eval(self.values[key].text())
            ret['properties'] = newProperties     
            
            parameters = dict()
            for key in self.valuesPar.keys():
                parameters[key] = eval(self.valuesPar[key].text())
            ret['parameters'] = parameters     
                
            return ret         
        else:
            return False
            
            
class convertSymDialog(QtWidgets.QDialog):
    def __init__(self, title='Convert Symbol', size=(400, 300), parent=None): 
        super(convertSymDialog, self).__init__(parent)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        # edit widget
        self.layout.addWidget(QtWidgets.QLabel('Name'))

        self.text_name = QtWidgets.QLineEdit(parent)
        font = QtGui.QFont()
        font.setFamily('Lucida')
        font.setFixedPitch(True)
        font.setPointSize(12)
        self.text_name.setFont(font)
        self.layout.addWidget(self.text_name)
        
        self.layout.addWidget(QtWidgets.QLabel('Icon'))
        self.text_icon = QtWidgets.QWidget()
        self.icon_layout = QtWidgets.QHBoxLayout()
        self.icon_createBtn = QtWidgets.QPushButton('Create Icon')    
        self.icon_selectIcon = QtWidgets.QPushButton('Select Icon')
        self.icon_selectIcon.clicked.connect(self.selectIcon)        
#        self.icon_layout.addWidget(self.icon_createBtn)
        self.icon_layout.addWidget(self.icon_selectIcon)
        self.text_icon.setLayout(self.icon_layout)
        self.layout.addWidget(self.text_icon)        
        
#        self.layout.addWidget(QtWidgets.QLabel('Parameters'))
#        self.text_parameters = QtWidgets.QWidget()
#        self.parameter_layout = QtWidgets.QHBoxLayout()
#        self.parameter_inp = QtWidgets.QCheckBox('input')
#        self.parameter_outp = QtWidgets.QCheckBox('output')
#        self.parameter_layout.addWidget(self.parameter_inp)
#        self.parameter_layout.addWidget(self.parameter_outp)
#        self.text_parameters.setLayout(self.parameter_layout)
#        self.layout.addWidget(self.text_parameters)
        
        
#        
#        myFont=QtGui.QFont()
#        myFont.setBold(True)
#        self.label.setFont(myFont)        
        
        self.layout.addWidget(QtWidgets.QLabel('Properties'))
        self.text_properties = QtWidgets.QWidget()
        
        self.grid = QtWidgets.QGridLayout()
        self.values = dict()
        self.n = 0
        
        self.key_field = QtWidgets.QLineEdit('key')
        self.addProperty = QtWidgets.QPushButton('Add property')
        self.addProperty.clicked.connect(self.addPropertyAction)  
        self.grid.addWidget(self.key_field,99,0)
        self.grid.addWidget(self.addProperty,99,1)
        
        
        
        self.text_properties.setLayout(self.grid)
        self.layout.addWidget(self.text_properties)


          
        
#        self.layout.addWidget(QtWidgets.QLabel('Properties'))
#        self.text_properties = QtWidgets.QTextEdit(parent)
#        font = QtGui.QFont()
#        font.setFamily('Lucida')
#        font.setFixedPitch(True)
#        font.setPointSize(12)
#        self.text_properties.setFont(font)
#        self.layout.addWidget(self.text_properties)
        
        # Cancel and OK buttons
        buttons = QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Cancel
        self.bbox = QtWidgets.QDialogButtonBox(buttons)
        self.bbox.accepted.connect(self.accept)
        self.bbox.rejected.connect(self.reject)
        self.layout.addWidget(self.bbox)

        # set window title and window size
        self.setWindowTitle(title)
        self.resize(size[0], size[1]) 
        self.filename = (0,0)  
    
    def selectIcon(self):
        self.filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open',respath + '/blocks/', filter='*.svg')
    
    
    
    def addPropertyAction(self):
        key = self.key_field.text()
        Lab = QtWidgets.QLabel(key)
        Val = QtWidgets.QLineEdit('0')
        self.values[key] = Val
        self.grid.addWidget(Lab,self.n,0)
        self.grid.addWidget(Val,self.n,1)
        self.n += 1

    def getRet(self):
        if self.exec_():
            ret = dict()
            if not self.text_name.text():
                error('Name required')
                return False
            if not re.match(r'[a-z_]\w*$', self.text_name.text(), re.I):
                error('No valid variable name')
                return False
            if self.filename:
                ret['icon'] = QtCore.QFileInfo(self.filename).baseName()
            else:
                ret['icon']= None 
                error('No icon selected', warn=True)
            
            ret['name'] = self.text_name.text()
            
            newProperties = dict()
            for key in self.values.keys():
                newProperties[key] = self.values[key].text()
            ret['properties'] = newProperties            
               
            return ret         
        else:
            return False
            
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    pins = [('i', -10, 10, 'pin1'), 
            ('i', -10, 50, 'pin2'), 
            ('o',  10, 30, 'pin3'),
            ('i', -10, 50, 'pin4'), 
            ('o',  10, 30, 'pin5'),
            ('i', -10, 50, 'pin6'), 
            ('o',  10, 30, 'bizarre_pin_name')]
            
    fmt = '{:^3} {: ^4} {: ^4} {}'
    t = [fmt.format(*'#io x y name'.split())]
    for pt, x, y, pn in pins:
        t.append(fmt.format(pt, x, y, pn))
    txt = '\n'.join(t)+ '\n'
        
    pe = txtDialog('Pineditor for block X')
#    txt = pe.editTxt(txt)
#    for line in txt.splitlines():
#        try:
#            pt, x, y, pn = line.split()
#            if not pt.startswith('#'):
#                print pt, x, y, pn
#        except:
#            print('ignored: ' + line)
            
    res = pe.editList(pins, header='io x y pinname')
    print(res)
    sys.exit(app.exec_())
