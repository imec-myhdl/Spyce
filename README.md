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

##Installing as super user:
1) download and untar pycontrol-gui.tgz ("tar xvfz pycontrol-gui.tgz")  
   alternatively you could use (needs git installed):  
   git clone https://github.com/imec-myhdl/pycontrol-gui.git
2) Become superuser
3) Install the files:  
   cd path_to_pycontrol_gui_folder  
   make install
4) Define this environment variables in your .bashrc file:  
   export PYSUPSICTRL=path_to_pycontrol_gui_folder  
   export PYEDITOR=emacs # or any other editor

##Installing as normal user (requires virtualenv installed):
1) download and untar pycontrol-gui.tgz ("tar xvfz pycontrol-gui.tgz")  
   alternatively you could use (needs git installed):  
   git clone https://github.com/imec-myhdl/pycontrol-gui.git
2) create a virtual environment:
```
mkvirtualenv env_pycontrol
```
you can enter and exit the new environment with these two commands
```
deactivate # will exit to the normal environment
workon env_pycontrol # activate the environment (stored in ~/.virtualenvs)
```
3) install the missing dependencies with pip (they will be in your virtual_env, rather than the system-wide installation). Example:
```
pip install git+https://github.com/python-control/python-control
pip install git+https://github.com/jgoppert/Slycot
```
4) install supsi modules
```
# control module
cd toolbox/supsictrl; python setup.py install --record installed-files.txt
cd toolbox/supsisim; python setup.py install --record installed-files.txt
```
   A later uninstall can be done with:
```
cd toolbox/supsictrl
cat installed-files.txt|xargs rm # remove the files

cd toolbox/supsisim
cat installed-files.txt|xargs rm # remove the files
```



17.04.2016 roberto.bucher@supsi.ch
