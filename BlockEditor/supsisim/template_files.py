# -*- coding: utf-8 -*-
"""
Created on Wed Nov 28 11:17:33 2018

@author: paul
"""

_templates = dict()

#==============================================================================
#  Block template
#==============================================================================
#  available fields for netlist templates:
#   name
#   libname
#   inp
#   outp
#   io
#   bbox
#   parameters
#   properties
#   views
# 
#==============================================================================
_templates['block'] = """# block definition
# name = '{name}'
# libname = '{libname}'

inp  = {inp}
outp = {outp}
# io   = {io}

bbox = {bbox}

parameters = {parameters} # pcell if not empty
properties = {properties} # netlist properties

#view variables:
views = {views}
"""
_templates['diagram'] = """# diagram {name}
# auto-generated, hand edits will be lost

blocks = []

connections = []

nodes = []

comments = []
"""

#==============================================================================
# Netlits templates
#==============================================================================
#  available fields for netlist templates:
#    body            - netlist that was created
#    projectname      
#    version          
#    copyrightText    
#    copyrightPolicy  
#    ticks_per_second 
#    t_stop           
#    blockname        
#    user             
#    t_resolution     - string e.g. 1fs if ticks_per_second == 1e15
# 
#==============================================================================
_templates['myhdl'] = """
#---------------------------------------------------------------------------------------------------
# Project   : {projectname}
# Filename  : {blockname}.py
# Version   : {version}
# Author    : {user}
# Contents  : MyHDL model for {blockname}
# Copyright : {copyrightText}
#             *** {copyrightPolicy} ***
#---------------------------------------------------------------------------------------------------

TIME_UNIT = {ticks_per_second:g}
{include}

{body}

"""

_templates['myhdl_toplevel_include'] = ''

_templates['myhdl_include'] = ''

# test bench
_templates['myhdl_tbfooter'] = """
    
if __name__ == "__main__":
# =============================================================================
#     setup and run testbench
# =============================================================================

    from myhdl import traceSignals    
    {blockname}_tb = {blockname} # append "_tb"
    tb = {blockname}_tb()
    traceSignals.timescale = '{t_resolution}s'    
    tb.config_sim(trace=True)
    tb.run_sim(duration = {t_stop} * TIME_UNIT)

"""

_templates['systemverilog'] = """
//--------------------------------------------------------------------------------------------------
// Project   : {projectname}                                                                             
// Filename  : {blockname}.sv
// Version   : {version}                                                                             
// Author    : {user}
// Contents  : systemVerilog model for {blockname}
// Copyright : {copyrightText}                                     
//             *** {copyrightPolicy} ***
//--------------------------------------------------------------------------------------------------
`timescale 1ps/{t_resolution}
{include}

{body}

"""

_templates['systemverilog_toplevel_include'] = ''

_templates['systemverilog_include'] = ''

_templates['systemverilog_tbfooter'] = ''
