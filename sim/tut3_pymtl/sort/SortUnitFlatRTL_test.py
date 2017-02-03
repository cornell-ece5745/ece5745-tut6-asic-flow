#=========================================================================
# SortUnitFlatRTL_test
#=========================================================================

import pytest

from copy            import deepcopy
from random          import randint

from pymtl           import *
from pclib.test      import run_test_vector_sim
from SortUnitCL_test import mk_test_vector_table
from SortUnitFlatRTL import SortUnitFlatRTL

#-------------------------------------------------------------------------
# Syntax helpers
#-------------------------------------------------------------------------

# We define the header string here since it is so long. Then reference
# the header string and include a comment to label each of the columns.

header_str = \
  ( "in_val",   "in_[0]",  "in_[1]",  "in_[2]",  "in_[3]",
    "out_val*", "out[0]*", "out[1]*", "out[2]*", "out[3]*" )

# We define a global variable 'x' so that we can simply use the x
# character instead of '?' to indicate don't care reference outputs

x = '?'

# Use xr as shorthand for xrange to make list comprehensions more compact

xr = xrange

#-------------------------------------------------------------------------
# test_basic
#-------------------------------------------------------------------------

def test_basic( dump_vcd, test_verilog ):
  run_test_vector_sim( SortUnitFlatRTL(), [ header_str,
    # in  in  in  in  in  out out out out out
    # val [0] [1] [2] [3] val [0] [1] [2] [3]
    [ 0,  0,  0,  0,  0,  0,  x,  x,  x,  x ],
    [ 1,  4,  2,  3,  1,  0,  x,  x,  x,  x ],
    [ 0,  0,  0,  0,  0,  0,  x,  x,  x,  x ],
    [ 0,  0,  0,  0,  0,  0,  x,  x,  x,  x ],
    [ 0,  0,  0,  0,  0,  1,  1,  2,  3,  4 ],
    [ 0,  0,  0,  0,  0,  0,  x,  x,  x,  x ],
  ], dump_vcd, test_verilog )

#-------------------------------------------------------------------------
# test_stream
#-------------------------------------------------------------------------

def test_stream( dump_vcd, test_verilog ):
  run_test_vector_sim( SortUnitFlatRTL(), mk_test_vector_table( 3, [
    [ 4, 3, 2, 1 ], [ 9, 6, 7, 1 ], [ 4, 8, 0, 9 ]
  ]), dump_vcd, test_verilog )

#-------------------------------------------------------------------------
# test_dups
#-------------------------------------------------------------------------

def test_dups( dump_vcd, test_verilog ):
  run_test_vector_sim( SortUnitFlatRTL(), mk_test_vector_table( 3, [
    [ 2, 8, 9, 9 ], [ 2, 8, 2, 8 ], [ 1, 1, 1, 1 ]
  ]), dump_vcd, test_verilog )

#-------------------------------------------------------------------------
# test_sorted
#-------------------------------------------------------------------------

def test_sorted( dump_vcd, test_verilog ):
  run_test_vector_sim( SortUnitFlatRTL(), mk_test_vector_table( 3, [
    [ 1, 2, 3, 4 ], [ 1, 3, 5, 7 ], [ 4, 3, 2, 1 ]
  ]), dump_vcd, test_verilog )

#-------------------------------------------------------------------------
# test_random
#-------------------------------------------------------------------------

def test_random( dump_vcd, test_verilog ):
  tvec_random = [ [ randint(0,0xff) for i in xr(4) ] for y in xr(20) ]
  run_test_vector_sim( SortUnitFlatRTL(),
    mk_test_vector_table( 3, tvec_random ), dump_vcd, test_verilog )

