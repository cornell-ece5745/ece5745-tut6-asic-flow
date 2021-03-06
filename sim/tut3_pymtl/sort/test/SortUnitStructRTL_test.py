#=========================================================================
# SortUnitStructRTL_test
#=========================================================================

import pytest

from copy   import deepcopy
from random import randint

from pymtl3 import *
from pymtl3.stdlib.test_utils import run_test_vector_sim

from .SortUnitFL_test import header_str, mk_test_vector_table, x, \
                             tvec_stream, tvec_dups, tvec_sorted, tvec_random

from ..SortUnitStructRTL import SortUnitStructRTL

#-------------------------------------------------------------------------
# test_basic
#-------------------------------------------------------------------------

def test_basic( cmdline_opts ):
  run_test_vector_sim( SortUnitStructRTL(), [ header_str,
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
  run_test_vector_sim( SortUnitStructRTL(), mk_test_vector_table( 3, tvec_stream ),
                       cmdline_opts )

#-------------------------------------------------------------------------
# test_dups
#-------------------------------------------------------------------------

def test_dups( cmdline_opts ):
  run_test_vector_sim( SortUnitStructRTL(), mk_test_vector_table( 3, tvec_dups ),
                       cmdline_opts )

#-------------------------------------------------------------------------
# test_sorted
#-------------------------------------------------------------------------

def test_sorted( cmdline_opts ):
  run_test_vector_sim( SortUnitStructRTL(), mk_test_vector_table( 3, tvec_sorted ),
                       cmdline_opts )

#-------------------------------------------------------------------------
# test_random
#-------------------------------------------------------------------------

@pytest.mark.parametrize( "nbits", [ 4, 8, 16, 32 ] )
def test_random( nbits, cmdline_opts ):
  tvec_random = [ [ randint(0,2**nbits-1) for _ in range(4) ] for _ in range(20) ]
  run_test_vector_sim( SortUnitStructRTL(nbits),
    mk_test_vector_table( 3, tvec_random ), cmdline_opts )
