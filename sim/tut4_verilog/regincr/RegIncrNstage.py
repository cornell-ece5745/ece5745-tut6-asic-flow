#=========================================================================
# RegIncrNstage
#=========================================================================
# Registered incrementer that is parameterized by the number of stages.

from pymtl3 import *
from pymtl3.passes.backends.verilog import *

class RegIncrNstage( VerilogPlaceholder, Component ):

  # Constructor

  def construct( s, nstages=2 ):

    # Port-based interface

    s.in_ = InPort ( 8 )
    s.out = OutPort( 8 )

    # Configurations

    s.set_metadata( VerilogPlaceholderPass.params, {
      'p_nstages' : nstages,
    })
