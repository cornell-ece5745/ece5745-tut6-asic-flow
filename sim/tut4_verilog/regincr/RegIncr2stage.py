#=========================================================================
# RegIncr2stage
#=========================================================================
# Two-stage registered incrementer that uses structural composition to
# instantitate and connect two instances of the single-stage registered
# incrementer.

import os
from pymtl3 import *
from pymtl3.passes.backends.verilog import *


class RegIncr2stage( VerilogPlaceholder, Component ):

  # Constructor

  def construct( s ):

    # Port-based interface

    s.in_ = InPort ( 8 )
    s.out = OutPort( 8 )
