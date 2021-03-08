#=========================================================================
# RegIncr
#=========================================================================
# This is a simple model for a registered incrementer. An eight-bit value
# is read from the input port, registered, incremented by one, and
# finally written to the output port.

from pymtl3 import *
from pymtl3.passes.backends.verilog import *

class RegIncr( VerilogPlaceholder, Component ):

  # Constructor

  def construct( s ):

    # Port-based interface

    s.in_ = InPort ( 8 )
    s.out = OutPort( 8 )

    # The port map by default uses the PyMTL3 port names
    # s.set_metadata( VerilogPlaceholderPass.port_map, {
    #   s.in_: 'in_',
    #   s.out: 'out',
    # })

    # has_clk and has_reset are True by default
    # s.set_metadata( VerilogPlaceholderPass.has_clk, True )
    # s.set_metadata( VerilogPlaceholderPass.has_reset, True )
