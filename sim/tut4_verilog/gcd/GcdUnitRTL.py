#=========================================================================
# GCD Unit RTL Model
#=========================================================================

import os
from pymtl3 import *
from pymtl3.stdlib import stream
from pymtl3.passes.backends.verilog import *

from .GcdUnitMsg  import GcdUnitMsgs

#=========================================================================
# GCD Unit RTL Model
#=========================================================================

class GcdUnitRTL( VerilogPlaceholder, Component ):

  # Constructor

  def construct( s ):

    # Interface

    s.recv = stream.ifcs.RecvIfcRTL( GcdUnitMsgs.req )
    s.send = stream.ifcs.SendIfcRTL( GcdUnitMsgs.resp )
