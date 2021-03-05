#=========================================================================
# SortUnitFlatRTL_test
#=========================================================================

import pytest

from copy               import deepcopy
from random             import randint

from pymtl3             import *
from pymtl3.stdlib.test_utils import run_test_vector_sim
from ..SortUnitFlatRTL   import SortUnitFlatRTL

from .SortUnitFL_test   import tvec_stream, tvec_dups, tvec_sorted, tvec_random
from .SortUnitCL_test   import mk_test_vector_table


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

def test_basic( cmdline_opts ):
  run_test_vector_sim( SortUnitFlatRTL(), [ header_str,
    # in  in  in  in  in  out out out out out
    # val [0] [1] [2] [3] val [0] [1] [2] [3]
    [ 0,  0,  0,  0,  0,  0,  x,  x,  x,  x ],
    [ 1,  4,  2,  3,  1,  0,  x,  x,  x,  x ],
    [ 0,  0,  0,  0,  0,  0,  x,  x,  x,  x ],
    [ 0,  0,  0,  0,  0,  0,  x,  x,  x,  x ],
    [ 0,  0,  0,  0,  0,  1,  1,  2,  3,  4 ],
    [ 0,  0,  0,  0,  0,  0,  x,  x,  x,  x ],
  ], cmdline_opts )

#-------------------------------------------------------------------------
# test_stream
#-------------------------------------------------------------------------

def test_stream( cmdline_opts ):
  run_test_vector_sim( SortUnitFlatRTL(), mk_test_vector_table( 3, tvec_stream ),
                       cmdline_opts )

#-------------------------------------------------------------------------
# test_dups
#-------------------------------------------------------------------------

def test_dups( cmdline_opts ):
  run_test_vector_sim( SortUnitFlatRTL(), mk_test_vector_table( 3, tvec_dups ),
                       cmdline_opts )

#-------------------------------------------------------------------------
# test_sorted
#-------------------------------------------------------------------------

def test_sorted( cmdline_opts ):
  run_test_vector_sim( SortUnitFlatRTL(), mk_test_vector_table( 3, tvec_sorted ),
                       cmdline_opts )

#-------------------------------------------------------------------------
# test_random
#-------------------------------------------------------------------------

@pytest.mark.parametrize( "nbits", [ 4, 8, 16, 32 ] )
def test_random( nbits, cmdline_opts ):
  tvec_random = [ [ randint(0,2**nbits-1) for _ in range(4) ] for _ in range(20) ]
  run_test_vector_sim( SortUnitFlatRTL(nbits),
    mk_test_vector_table( 3, tvec_random ), cmdline_opts )
