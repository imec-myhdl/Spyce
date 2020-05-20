Spyce, Simple python circuit editor
=============
A simulink like editor with MyHDL netlist support. Heavily borrowed from a project for pycontrol by Roberto Bucher
http://robertobucher.dti.supsi.ch/python/ for the SUPSI university. You will find many references to supsi :) and also
some remaining packages that we did not yet update or remove

The following packages should be installed on your PC

* Python 2.7+ or Python 3.5+
* PySide, PySide2, PyQt4 or PyQt5
* Qt.py wrapper around PySide, PySide2, PyQt4 or PyQt5(see https://github.com/mottosso/Qt.py)
* MyHDL (best with fixbv extension, see https://github.com/imec-myhdl/myhdl)
* LateX if you want to build the pdf documentation

* our setup is based on anaconda python 2.7 and PyQt4 


Installing as normal user:
--------------------------
1) Install Spyce (checkout with git)
```
   git clone https://github.com/imec-myhdl/Spyce.git
```
2) install the  dependencies with pip (assuming you are on python3):
```
   pip install Qt.py    # thin wrapper around PyQt3/5 Pyside/Pysisde2
   pip install pyside2  # python interface to Qt5
   pip install autopep8 # format block sources (on disk) conform pep8
   pip install svgwrite # interface to inkscape
   pip install lxml     # legacy blocks, will gradually be phased out

```

Workspace preparation
---------------------
```
   mkdir workdir
   cd workdir
   
   # optional: create settings.py
   # use this file to make local modifications to the defaults (in supsisim/const.py)
   
   # link common libraries
   mkdir libraries
   ln -s <path-to-spyce>/Spyce/BlockEditor/libraries/* libraries
```

Editor (standalone)
-------------------
To start the editor you do not need a setup/make step. You can run it can directly without installing.
```
cd workdir
python <path-to-spyce>/Spyce/BlockEditor/spyce.py

# or define an alias (e.g. in your ~/.bashrc):
alias spyce='python <path-to-spyce>/Spyce/BlockEditor/spyce.py'
cd workdir
spyce


```
Documentation (standalone)
--------------------------
```
cd <path-to-spyce>/Spyce/doc
make latexpdf # or make html whatever you prefer and is supported by sphinx
```
manual will be in build/latex/spyce.pdf

Warning:
--------
Dangerous software, do not run as superuser, and be aware that there are bugs that could cause lost work (save as wrong filename for example). UNDO function is not implemented.

20.05.2020 imec-nl
