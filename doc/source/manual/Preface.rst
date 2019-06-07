########
Overview
########

The goal of the spyce project is to empower hardware designers with
a tool that simplifies the communication between developers, and to
take away the tedious work of manually connecting modules and block. 

Spyce (**S**\ imple **py**\ thon **c**\ ircuit **e**\ ditor) is a free, open-source package 
using Python and Qt to create a schematic, hierarchical view of a 
hardware design. Spyce also provides a simple, extensible  netlist
generation to be able to simulate your design. For now the project is 
mainly targeting digital signal processing (simulink like) and using 
MyHDL as the main netlisting language, with systemverilog netlisting 
in the planning.

This project is based on the work of Robert Bucher 
(http://robertobucher.dti.supsi.ch/python/), and follows his 
naming conventions that are a bit ununsual in the hardware world. A
'diagram' is a collection of basic elements (blocks, connections and 
ports) that constitutes a design. This diagram is in fact a schematic
drawing. A 'Port' is anything that can be connected to. These can be 
pins on a block, pins to upper hierarchical levels, or nodes; that connect
wires.

*************
prerequisites
*************

Spyce requires:

- python 2.7 or 3.5+
- Qt.py: wrapper around PySide, PySide2, PyQt4 and PyQt5, see https://github.com/mottosso/Qt.py
- any of PySide, PySide2, PyQt4 and PyQt5
- myhdl + fixbv extension, see https://github.com/imec-myhdl/myhdl
- inkscape to edit icons, and convert to png
- openoffice is optional, but default configured as editor for documentation
- spyder3 is optional, but default configured as python editor.
- spinx and latex if you want to build the documentation

Spyce is developed on python 2.7 and PyQt5.5.1
Multiple selection (by holding down control-key) has been incorporated in Qt5.5. 
This functionality unfortunately was never backported to Qt4 (although a patch is available from
https://asmaloney.com/2015/01/code/qt-patches-qgraphicsview-qimagewriter)

**********
Installing
**********

Install source code::

    git clone https://github.com/imec-myhdl/Spyce.git
    
Build documentation::

    cd Spyce/doc
    make latexpdf # or html
    
Start Spyce::

    cd Spyce/BlockEditor
    python spyce.py
    



