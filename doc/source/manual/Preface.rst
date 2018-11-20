########
Overview
########

The goal of the spyce project is to empower hardware designers with
a tool that simplifies the communication between developers, and to
take away the tedious work of manually connecting modules and block. 

Spyce (simple python circuit editor) is a free, open-source package 
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