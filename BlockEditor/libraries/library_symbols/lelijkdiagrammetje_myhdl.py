
#---------------------------------------------------------------------------------------------------
# Project   : placeholder
# Filename  : lelijkdiagrammetje_myhdl.py
# Version   : 1.0
# Author    : jonathan
# Contents  : Python lelijkdiagrammetje model 
# Copyright : placeholder
#             *** placeholder ***
#---------------------------------------------------------------------------------------------------


#-- import -----------------------------------------------------------------------------------------

from libraries.library_testlib import module_myhdl as module
from libraries.library_symbols import module_myhdl as module
from libraries.library_nonlin import FMU_myhdl as FMU
from libraries.library_output import Plot_myhdl as Plot

from myhdl import Signal, instance, instances, block

#-- code ---------------------------------------------------------------------------------

@block
def lelijkdiagrammetje():

    
    
    
    
    module2 = module()
    module1 = module()
    FMU0 = FMU()
    Plot0 = Plot()
    module0 = module()
    
    
    
    return instances()    
    
if __name__ == "__main__":
# =============================================================================
#     setup and run testbench
# =============================================================================

    from myhdl import traceSignals    
    
    @block
    def lelijkdiagrammetje_tb():
        pass
        
    tb = lelijkdiagrammetje_tb()
    traceSignals.timescale = '1fs'    
    tb.config_sim(trace=True)
    tb.run_sim()
