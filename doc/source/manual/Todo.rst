####
TODO
####
.. index:: single: TODO

The drawing tool works, but is rather unpolished. Some features that I would like to see:

-   proper Undo:
    There has been some work, but when moving a component, Qt constantly emits 'changed' signals
    and that will spam the redrawing. Probably it is possible to suppress these whith button down/up
    
-   Git support:
    it should be possible to checkin/revert any block or diagram

-   connections:
    Connections as line-segments, but moving a segment should also move the vertices of the
    attached segments. This is not so straight-forward as it looks, especially when a segment is
    connected to a node or block-port

-   blocks: 
    the interface to a block is rather clumsy, passing attributes as a dictionary, where 
    python \*\*kwargs approch already provides the same functionality. Changing however is quite 
    some work due to all the libraries
    
-   inout ports:
    There are some hooks in the code to implement inout, but for now they are low priority. 
    
-   rotation:
    flipping is supported, it should not be too hard to add rotation (block, label, pin)


-  Probes:
   It is simple to hook-up any simulator, but the postprocessing requires 'software' measurement devices.
   These can be 'volt' meters, oscilloscopes, spectrum-analyzers, communications analyzer (i.e. a software receiver) etc.

- Sources: like probes there is also a need for software clock-sources, vector/data-generators etc.