#=========================================================================
# sort_sim_test
#=========================================================================
# Make sure that sort-sim works.

import pytest
import os

from subprocess import check_call, CalledProcessError
from itertools  import product

impls  = [ "fl", "cl", "rtl-flat", "rtl-struct" ]
inputs = [ "random", "sorted-rev", "sorted-fwd" ]

@pytest.mark.parametrize( "impl,input_", product(impls,inputs) )
def test( impl, input_, test_verilog ):

  # Get path to simulator script

  sim_dir = os.path.dirname( os.path.abspath( __file__ ) )
  sim     = sim_dir + os.path.sep + 'sort-sim'

  # Command

  cmd = [ sim, "--impl", impl, "--input", input_ ]

  # Handle test verilog

  if test_verilog:
    if impl.startswith("rtl"):
      cmd.append( "--translate" )
    else:
      pytest.skip("ignoring non-Verilog tests")

  # Display simulator command line

  print ""
  print "Simulator command line:", ' '.join(cmd)

  # Run the simulator

  try:
    check_call(cmd)
  except CalledProcessError as e:
    raise Exception( "Error running simulator!" )

