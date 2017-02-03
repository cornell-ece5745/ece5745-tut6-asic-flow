#=========================================================================
# SortUnitStructRTL
#=========================================================================

from pymtl import *

class SortUnitStructRTL( VerilogModel ):

  # Verilog module setup

  vprefix = "tut4_verilog_sort"
  vlinetrace = True

  # Constructor

  def __init__( s, nbits=8 ):

    # Interface

    s.in_val  = InPort (1)
    s.in_     = [ InPort  (nbits) for _ in range(4) ]

    s.out_val = OutPort(1)
    s.out     = [ OutPort (nbits) for _ in range(4) ]

    # Verilog parameters

    s.set_params({
      'p_nbits' : nbits,
    })

    # Verilog ports

    s.set_ports({
      'clk'     : s.clk,
      'reset'   : s.reset,
      'in_val'  : s.in_val,
      'in0'     : s.in_[0],
      'in1'     : s.in_[1],
      'in2'     : s.in_[2],
      'in3'     : s.in_[3],
      'out_val' : s.out_val,
      'out0'    : s.out[0],
      'out1'    : s.out[1],
      'out2'    : s.out[2],
      'out3'    : s.out[3],
    })

