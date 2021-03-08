#=========================================================================
# SortUnitStructRTL
#=========================================================================
# This model sorts four nbit elements into ascending order using a
# bitonic sorting network. We break the four elements into two pairs and
# sort each pair independently. Then we compare the smaller elements from
# each pair and the larger elements from each pair before arranging the
# middle two elements. This implementation uses structural composition of
# Reg and MinMax child models.

import os
from pymtl3 import *
from pymtl3.passes.backends.verilog import *

class SortUnitStructRTL( VerilogPlaceholder, Component ):

  # Constructor

  def construct( s, nbits=8 ):

    #---------------------------------------------------------------------
    # Interface
    #---------------------------------------------------------------------

    s.in_val  = InPort ()
    s.in_     = [ InPort (nbits) for _ in range(4) ]

    s.out_val = OutPort()
    s.out     = [ OutPort(nbits) for _ in range(4) ]

    #---------------------------------------------------------------------
    # Configurations
    #---------------------------------------------------------------------

    s.set_metadata( VerilogPlaceholderPass.params, { 'p_nbits' : nbits } )
    s.set_metadata( VerilogPlaceholderPass.port_map, {
      s.in_[0]  : 'in0',
      s.in_[1]  : 'in1',
      s.in_[2]  : 'in2',
      s.in_[3]  : 'in3',
      s.out[0]  : 'out0',
      s.out[1]  : 'out1',
      s.out[2]  : 'out2',
      s.out[3]  : 'out3',
    })
