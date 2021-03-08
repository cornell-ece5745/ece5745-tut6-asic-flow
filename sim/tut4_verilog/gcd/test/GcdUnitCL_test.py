#=========================================================================
# GcdUnitCL_test
#=========================================================================

import pytest

from pymtl3 import *
from pymtl3.stdlib.test_utils import run_sim
from ..GcdUnitCL import gcd_cl, GcdUnitCL

# Reuse cases from FL tests

from .GcdUnitFL_test import TestHarness, test_case_table

#-------------------------------------------------------------------------
# test_gcd_cl
#-------------------------------------------------------------------------

def test_gcd_cl_calc():
  #              a   b         result ncycles
  assert gcd_cl( 0,  0  ) == ( 0,     1       )
  assert gcd_cl( 1,  0  ) == ( 1,     1       )
  assert gcd_cl( 0,  1  ) == ( 1,     2       )
  assert gcd_cl( 5,  5  ) == ( 5,     3       )
  assert gcd_cl( 15, 5  ) == ( 5,     5       )
  assert gcd_cl( 5,  15 ) == ( 5,     6       )
  assert gcd_cl( 7,  13 ) == ( 1,     13      )
  assert gcd_cl( 75, 45 ) == ( 15,    8       )
  assert gcd_cl( 36, 96 ) == ( 12,    10      )

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test_gcd_cl( test_params ):

  th = TestHarness( GcdUnitCL() )

  th.set_param("top.src.construct",
    msgs=test_params.msgs[::2],
    initial_delay=test_params.src_delay,
    interval_delay=test_params.src_delay )

  th.set_param("top.sink.construct",
    msgs=test_params.msgs[1::2],
    initial_delay=test_params.sink_delay,
    interval_delay=test_params.sink_delay )

  run_sim( th )
