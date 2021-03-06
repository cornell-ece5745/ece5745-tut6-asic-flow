#=========================================================================
# SortUnitCL_test
#=========================================================================

import pytest

from pymtl3      import *
from pymtl3.stdlib.test_utils import run_test_vector_sim, mk_test_case_table

from .SortUnitFL_test import header_str, mk_test_vector_table, x, \
                             tvec_stream, tvec_dups, tvec_sorted, tvec_random

from ..SortUnitCL import SortUnitCL

#-------------------------------------------------------------------------
# test_basic
#-------------------------------------------------------------------------

def test_basic():
  run_test_vector_sim( SortUnitCL(), [ header_str,
    # in  in  in  in  in  out out out out out
    # val [0] [1] [2] [3] val [0] [1] [2] [3]
    [ 0,  0,  0,  0,  0,  0,  x,  x,  x,  x ],
    [ 1,  4,  2,  3,  1,  0,  x,  x,  x,  x ],
    [ 0,  0,  0,  0,  0,  0,  x,  x,  x,  x ],
    [ 0,  0,  0,  0,  0,  0,  x,  x,  x,  x ],
    [ 0,  0,  0,  0,  0,  1,  1,  2,  3,  4 ],
    [ 0,  0,  0,  0,  0,  0,  x,  x,  x,  x ],
  ] )

#-------------------------------------------------------------------------
# Parameterized Testing with Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (                 "nstages inputs      "),
  [ "1stage_stream", 1,      tvec_stream  ],
  [ "1stage_dups",   1,      tvec_dups    ],
  [ "1stage_sorted", 1,      tvec_sorted  ],
  [ "1stage_random", 1,      tvec_random  ],
  [ "2stage_stream", 2,      tvec_stream  ],
  [ "2stage_dups",   2,      tvec_dups    ],
  [ "2stage_sorted", 2,      tvec_sorted  ],
  [ "2stage_random", 2,      tvec_random  ],
  [ "3stage_stream", 3,      tvec_stream  ],
  [ "3stage_dups",   3,      tvec_dups    ],
  [ "3stage_sorted", 3,      tvec_sorted  ],
  [ "3stage_random", 3,      tvec_random  ],
])
@pytest.mark.parametrize( **test_case_table )
def test_sort_cl( test_params ):
  nstages = test_params.nstages
  inputs  = test_params.inputs
  run_test_vector_sim( SortUnitCL( nstages=nstages ),
    mk_test_vector_table( nstages, inputs ) )

#-------------------------------------------------------------------------
# Parameterized Testing of With nstages = [ 1, 2, 3, 4, 5, 6 ]
#-------------------------------------------------------------------------

@pytest.mark.parametrize( "n", [ 1, 2, 3, 4, 5, 6 ] )
def test_sort_cl_random( n ):
  run_test_vector_sim( SortUnitCL( nstages=n ),
    mk_test_vector_table( n, tvec_random ) )

