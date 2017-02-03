#=========================================================================
# SortUnitFL_test
#=========================================================================

from copy       import deepcopy
from random     import randint

from pymtl      import *
from pclib.test import run_test_vector_sim
from SortUnitFL import SortUnitFL

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

#-------------------------------------------------------------------------
# test_basic
#-------------------------------------------------------------------------

def test_basic( dump_vcd ):
  run_test_vector_sim( SortUnitFL(), [ header_str,
    # in  in  in  in  in  out out out out out
    # val [0] [1] [2] [3] val [0] [1] [2] [3]
    [ 0,  0,  0,  0,  0,  0,  x,  x,  x,  x ],
    [ 1,  4,  2,  3,  1,  0,  x,  x,  x,  x ],
    [ 0,  0,  0,  0,  0,  1,  1,  2,  3,  4 ],
    [ 0,  0,  0,  0,  0,  0,  x,  x,  x,  x ],
  ], dump_vcd )

#-------------------------------------------------------------------------
# test_stream
#-------------------------------------------------------------------------

def test_stream( dump_vcd ):
  run_test_vector_sim( SortUnitFL(), [ header_str,
    # in  in  in  in  in  out out out out out
    # val [0] [1] [2] [3] val [0] [1] [2] [3]
    [ 0,  0,  0,  0,  0,  0,  x,  x,  x,  x ],
    [ 1,  2,  8,  9,  3,  0,  x,  x,  x,  x ],
    [ 1,  9,  3,  4,  5,  1,  2,  3,  8,  9 ],
    [ 1,  4,  7,  3,  8,  1,  3,  4,  5,  9 ],
    [ 0,  0,  0,  0,  0,  1,  3,  4,  7,  8 ],
    [ 0,  0,  0,  0,  0,  0,  x,  x,  x,  x ],
  ], dump_vcd )

#-------------------------------------------------------------------------
# test_dups
#-------------------------------------------------------------------------

def test_dups( dump_vcd ):
  run_test_vector_sim( SortUnitFL(), [ header_str,
    # in  in  in  in  in  out out out out out
    # val [0] [1] [2] [3] val [0] [1] [2] [3]
    [ 0,  0,  0,  0,  0,  0,  x,  x,  x,  x ],
    [ 1,  8,  8,  8,  2,  0,  x,  x,  x,  x ],
    [ 1,  9,  3,  3,  9,  1,  2,  8,  8,  8 ],
    [ 1,  1,  1,  1,  1,  1,  3,  3,  9,  9 ],
    [ 0,  0,  0,  0,  0,  1,  1,  1,  1,  1 ],
    [ 0,  0,  0,  0,  0,  0,  x,  x,  x,  x ],
  ], dump_vcd )

#-------------------------------------------------------------------------
# test_random
#-------------------------------------------------------------------------

def test_random( dump_vcd ):

  test_vector_table = [ header_str,
    # in  in  in  in  in  out out out out out
    # val [0] [1] [2] [3] val [0] [1] [2] [3]
    [ 0,  0,  0,  0,  0,  0,  x,  x,  x,  x ],
    [ 1,  0,  0,  0,  0,  0,  x,  x,  x,  x ],
  ]

  last_results = [ 0, 0, 0, 0 ]
  for i in xrange(20):
    inputs = [ randint(0,0xff) for i in xrange(4) ]
    test_vector_table.append( [1] + inputs + [1] + last_results )
    last_results = deepcopy( sorted(inputs) )

  run_test_vector_sim( SortUnitFL(), test_vector_table, dump_vcd )

