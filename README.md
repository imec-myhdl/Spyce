# pycontrol-gui
a pycontrol distro with a simulink like editor

The following packages should be installed on your PC

* numpy
* scipy
* matplotlib
* python-control   https://github.com/python-control/python-control
* Slycot Master    https://github.com/jgoppert/Slycot
* python-qt4
* python-qt4-dev
* python-qwt
* python-setuptools
* python-lxml
* liblapack-dev

Install the packages:
1) untar pycontrol.tgz ("tar xvfz pycontrol.tgz")
2) Become superuser
3) Install the files:  
   cd path_to_pycontrol_gui_folder  
   make install
4) Define this environment variables in your .bashrc file:  
   export PYSUPSICTRL=path_to_pycontrol_gui_folder  
   export PYEDITOR=emacs

"emacs" can be substituted by another editor

17.04.2016 roberto.bucher@supsi.ch
