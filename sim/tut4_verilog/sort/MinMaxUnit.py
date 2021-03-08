#=========================================================================
# MinMaxUnit
#=========================================================================
# This module takes two inputs, compares them, and outputs the larger
# via the "max" output port and the smaller via the "min" output port.

import os
from pymtl3 import *
from pymtl3.passes.backends.verilog import *

class MinMaxUnit( VerilogPlaceholder, Component ):

  # Constructor

  def construct( s, nbits ):

    # Port-based interface

    s.in0     = InPort ( nbits )
    s.in1     = InPort ( nbits )
    s.out_min = OutPort( nbits )
    s.out_max = OutPort( nbits )

    # Configurations

    s.set_metadata( VerilogPlaceholderPass.params, { 'p_nbits' : nbits } )
