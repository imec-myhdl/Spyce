#!/usr/bin/python
# aim for python 2/3 compatibility
from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

from  Qt import QtGui, QtWidgets, QtCore # see https://github.com/mottosso/Qt.py
import sys, os
#if sys.version_info>(3,0):
#    import sip
#    sip.setapi('QString', 1)
#
from supsisim.const import path,respath

class LibraryChoice_Dialog(QtWidgets.QMessageBox):
    def __init__(self,parent=None):
        super(LibraryChoice_Dialog,self).__init__(parent)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setWindowTitle('Library')
        self.setText("What library would you like to use")
        self.addButton('List view',self.YesRole)
        self.addButton('Symbol view',self.NoRole)
        
        

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

class labelDialog(QtWidgets.QDialog):
    def __init__(self, title='Add Label', size=(300, 100), parent=None):
        super(labelDialog, self).__init__(parent)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        
        self.layout.addWidget(QtWidgets.QLabel('Label:'))
        # edit widget
        self.text_edit = QtWidgets.QLineEdit(parent)
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
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.viewWidgets = []

        import supsisim.const
        reload(supsisim.const)
        from supsisim.const import viewEditors        
        
        views = dict(viewEditors)
        # edit widget
        for key in views.keys():
            view = QtWidgets.QWidget()
            viewLayout = QtWidgets.QHBoxLayout()
            view.setLayout(viewLayout)
            
            viewLayout.addWidget(QtWidgets.QLabel(key + ":"))
    
            text_name = QtWidgets.QLineEdit(views[key])
            font = QtGui.QFont()
            font.setFamily('Lucida')
            font.setFixedPitch(True)
            font.setPointSize(12)
            text_name.setFont(font)
            viewLayout.addWidget(text_name)
            
            self.layout.addWidget(view)
            self.viewWidgets.append(dict(key=key,widget=text_name))
        
        
        # Cancel and OK buttons
        buttons = QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Cancel
        self.bbox = QtWidgets.QDialogButtonBox(buttons)
        self.bbox.accepted.connect(self.accept)
        self.bbox.rejected.connect(self.reject)
        self.layout.addWidget(self.bbox)

        # set window title and window size
        self.setWindowTitle(title)
        self.resize(size[0], size[1])   
    
    
    
    def getRet(self):
        if self.exec_():
            ret = []
            for i,value in enumerate(self.viewWidgets):
                ret.append(dict(key=value['key'],text=value['widget'].text()))
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
        
        self.layout.addWidget(QtWidgets.QLabel('Parameters'))
        self.text_parameters = QtWidgets.QWidget()
        self.parameter_layout = QtWidgets.QHBoxLayout()
        self.parameter_inp = QtWidgets.QCheckBox('input')
        self.parameter_outp = QtWidgets.QCheckBox('output')
        self.parameter_layout.addWidget(self.parameter_inp)
        self.parameter_layout.addWidget(self.parameter_outp)
        self.text_parameters.setLayout(self.parameter_layout)
        self.layout.addWidget(self.text_parameters)
        
        self.layout.addWidget(QtWidgets.QLabel('Properties'))
        self.text_properties = QtWidgets.QTextEdit(parent)
        font = QtGui.QFont()
        font.setFamily('Lucida')
        font.setFixedPitch(True)
        font.setPointSize(12)
        self.text_properties.setFont(font)
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
    
    def selectIcon(self):
        self.filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open',respath + '/blocks/', filter='*.svg')
    
    def getRet(self):
        if self.exec_():
            ret = dict()
            ret['name'] = self.text_name.text()
            parameters = []
            if self.parameter_inp.isChecked():
                parameters.append('input') 
            if self.parameter_outp.isChecked():
                parameters.append('output') 
            ret['parameters'] = parameters
            ret['properties'] = self.text_properties.toPlainText() if self.text_properties.toPlainText() else '[]'
            ret['icon'] = QtCore.QFileInfo(self.filename[0]).baseName()
    
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
