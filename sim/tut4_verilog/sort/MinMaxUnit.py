#=========================================================================
# MinMaxUnit
#=========================================================================

from pymtl import *
import os

class MinMaxUnit( VerilogModel ):

  # Verilog module setup

  vprefix = "tut4_verilog_sort"

  # Constructor

  def __init__( s, nbits=8 ):

    s.in0     = InPort  ( nbits )
    s.in1     = InPort  ( nbits )
    s.out_min = OutPort ( nbits )
    s.out_max = OutPort ( nbits )

    # Verilog parameters

    s.set_params({
      'p_nbits' : nbits,
    })

    # Verilog ports

    s.set_ports({
      'in0'     : s.in0,
      'in1'     : s.in1,
      'out_min' : s.out_min,
      'out_max' : s.out_max,
    })

  # Line tracing

  def line_trace( s ):
    return "{}|{}(){}|{}".format( s.in0, s.in1, s.out_min, s.out_max )


