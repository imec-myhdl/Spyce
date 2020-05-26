###################
Building components
###################
.. index:: single: Building components
******
Blocks
******

.. index:: single: Blocks

Blocks are symbolic representations of circuit modules. A block must contain a number
of standard elements like pins, but can also include optional elements like tooltip or
netlisting functions.


Parameters and properties
=========================

Blocks can have both parameters and properties. They control the behaviour of the 
block, The difference is that a parameter can change the *interface* of the blocks:
pin names, or number of pins. Properties *can* change the symbol, but *not* the pins.
Both properties and parameters are passed to the netlist. A paramerized Block is a block containing
a non empty *parameters* variable

Creating Blocks with the GUI
============================

There are two ways to create a Block: either via the *import MyHdl* function or manually via the *Create Block* function.

If you already have a MyHdl file, you can create a Block (symbolic view) by importing it.
In the library viewer select the destination library, and then click on the *import Myhdl* icon.
The import routine will guess in and outputs, but might get it wrong, so you might want to edit the pins or their positions.
Note that any keyword arguments are treated as properties. You can check the created block by right-clicking on the new block 
and selecting views->blk_source, which will pop up the prefered editor

In the library viewer right-click somewhere in empty space and choose *Create block*.
You can choose an icon if you can re-use an existing icon (but most of the time you 
will create a new one later). You add inputs, outputs, parameters and properties. 
After clicking OK the block is created in the current library.

When you right click on a block you can choose:

*edit icon*  to edit the icon, or generate an empty svg drawing when it is not yet present. 

*Edit pins* to edit pin-names and pin-positions, or add/delete pins

*Change BBox* to edit the bounding box

*Views* will allow you to edit any of the other views


Creating Blocks from code
=========================

Blocks are simple python files that are inside a 'library'. The blocks should *not* import 
Qt as the netlister must be able to import them, without a gui. If Qt is needed or modules that import Qt
the easiest solution is to import them in the function that needs them (but never in the main, or netlist
routines). An Example::
    # cell definition
    # name = 'myblock'
    # libname = 'mylibrary'
    
    tooltip = 'This is an empty block with inputs a and b and output z'

    inp  = [('a', -40, -20), ('b', -40, 20)]
    outp = [('z', 40, 0)]
    io   = []
    bbox = None

    parameters = {} # pcell if not empty
    properties = {} # netlist properties

    #view variables:
    views = {'icon':'myblock.svg'}

.. py:data:: inp
.. py:data:: outp
.. py:data:: inout

*inp, outp, inout* are lists of tuples (pinname, x, y). The pinname can start with a `'.'` to indicate that the label should not be displayed. 
Alternatively *inp, outp, inout* can be an integer, being the number if inputs/outputs or inouts. The actual pins will be named '.i_0', '.i_1' 
etc. for inputs, '.o_0', '.o_1' etc. for outputs, or '.io_0', '.io_1' etc. for inouts. Note: inouts are optional and not yet properly implemented.

.. py:data:: tooltip
*tooltip* is an optional string that will be displayed when the mouse hoovers on the block.

.. py:data:: views
*views* is a dictionary that contains all (other) views. If *views['icon']* is defined it looks for
an svg file in either the *resources/blocks* directory (when no extension is specified) or in the same directory (library) as the block code otherwise.

.. py:data:: bbox
*bbox* is either *None*, or a 4-tuple: *(left, top, width, height)*

.. py:function:: ports(param)
This (optional, but highly recommended) function must return a tuple (inp, outp, inout), 
based on the parameters in the dictionary 'param'. Each of inp, outp, inout is a list of tuples 
(pinname, x, y). The pinname can start with a `'.'` to indicate that the label should not be displayed

.. py:function:: getSymbol(param, properties,parent=None,scene=None)
This function returns a :class:`Block` object. It is mandatory for parametrized blocks.
The getSymbol function will probably start with importing the block class, and Qt

.. py:function:: toMyhdlInstance(instname, connectdict, param)
.. index:: single: toMyhdlInstance

This function is optionally, but mandatory when (myhdl)netlisting parametrized blocks. It should either return a 
properly indented string (4 leading spaces) containing the MyHDL code or a dictionary (see below). 


*toMyhdlInstance* requires the following arguments:

- instance name is a string with the name of the block in the diagram. 
- connectdict is a dictionary with connections and properties (connectdict[pinname] = nettname or connectdict[property_name] = property_value). 
  This choice was made since they are both elements of an instantiation e.g. b1ock1_instance = myBlock(signal_1, signal_2, property_1=42)
- param is a dictionary with all the parameters    

When *toMyhdlInstance* returns a dictionary the keys represent paths, and values the (literal) content of submodules of the netlist. 
These will be stored as a module in the given location (relative to netlist dir) and if needed an empty *__init__.py* will be created.
There are several special cases:

- '__defs__': the entry contains a properly indented string (4 leading spaces) that will be included in the top section of the netlist, 
  prior to the signal definitions. Any variable that is defined may be used in signal definitions. 
- '__signals__': the entry contains a properly indented string (4 leading spaces) that will be included in the top section of the netlist, 
  that normally contains the signal definitions.
- '__main__': the entry contains a properly indented string (4 leading spaces) containing code to be included in the main section of the netlist,
  that normally contains the instances.
- '__expr__': the entry is a dictionary where the keys are the netnames and the values are the expressions that need to be evaluated.
  This is only useful for signals that are combinatorial expressions of other signals. As an example how to use this look at the Sum block in the math library.

note: spyce always netlists with the *pin_name = connected_signal_name* syntax to remove all ambiguity

.. py:function:: toSystemVerilogInstance(instname, connectdict, param)
.. index:: single: toSystemVerilogInstance
This function is optionally, but mandatory when (systemVerilog)netlisting parametrized blocks. It should either return a 
properly indented string (4 leading spaces) containing the systemVerilog code or a dictionary (this function is mostly identical to 
*toMyhdlInstance*). Note: not yet implemented.

After importing a block the following attributes are added:

.. py:data:: blk.blockname
This is the name of the module (without the .py extension)

.. py:data:: blk.libname
This is the name of the directory of the module (without the `'library_'` prefix)

.. py:data:: blk.views
the dictionary *views* will be extended with all views that are found (including the block-source itself)

