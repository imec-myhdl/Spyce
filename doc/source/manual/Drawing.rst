#######
Drawing
#######
.. index:: single: Drawing


Adding blocks
=============
.. index:: single: Adding blocks

Blocks can be dragged from the library viewer and dropped on the editor. Right-click on a block in 
the Editor will show all options. (note that adding parameters is not supported, only changing). 
Input pins are shown as little arrow heads, and outputs as little squares. 

Changing the name can be done directly by clicking in the text-label below a block, or via the 
right-click menu. The block can be flipped in the x direction, to enhance the readability.

Double clicking on a block will open the diagram view (if there is one), effectively descending one
level


Adding connections
==================
.. index:: single: Adding connections

To draw a connection you have to click on a block output, a node or an input pin. Double click will 
end the connection with the insertion of a node, and will pop up the edit-node menu to add a label 
or other properties. A connection can also be finished by clicking on a block-input, node or output pin

Adding pins
===========
To add a pin click on the pin symbol in the tool bar at the top of the editor. When the mouse is moved
to the drawing area and clicked the pin will be 'dropped' on the place of the cursor. Right click on 
the pin will show an edit menu (to add a pin label, or change the pin-type) and an entry to add a 
signalType. 

*signalType* can be any myhdl type, like *intbv(0,min=-12,max=12)* or *bool(1)*. It is used to initialize the
Signal() of the net for the netlisting.

*pin-label* should either be a valid identifier (starting with a letter or underscore) or a number. In the latter case the net is take to be a constant rather than a Signal during netlisting.

Adding comments
===============
Comments can be added by clicking on the text-balloon symbol in the tool bar at the top of the editor. 
When the mouse is moved to the drawing area and clicked the comment will be 'dropped' on the place of 
the cursor.

Double cicking on any editable label will pop up a font configuration diagram. 

Adding nodes
============
A node can be added by right-clicking in the diagram and choosing *Insert node*

Adding a node name/signal_type
==============================
A netname can be added by right clicking on a node, and selecting *Edit*. 
The field Pin_label can be used to enter the name. With the Pin_type the node type can be selected.
Default (node) puts the label at the top of the node. Choose nodeL, nodeR or nodeB for a label left, 
right or below the node. Net_names can be put in curly braces ( '{' and '}' ). This signals that the 
connection is an expression rather than an instance. This can only work with combinatorial blocks, 
and the driving block must support it in the toMyhdlInstance routine. see Blocks, section 
Creating Blocks from code.

A netsignal type can be added by right clicking on a node and selecting *Add/Edit signal type*.
Nets without a definition will be assumed boolean.
