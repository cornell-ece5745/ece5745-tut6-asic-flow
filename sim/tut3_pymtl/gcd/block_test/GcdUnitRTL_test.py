#=========================================================================
# GcdUnitRTL_test
#=========================================================================

import pytest

from pymtl3 import *
from pymtl3.stdlib.test_utils import run_sim
from ..GcdUnitRTL import GcdUnitRTL

# Reuse tests from FL model

from .GcdUnitCL_test import TestHarness, test_case_table

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test_gcd_rtl( test_params, cmdline_opts ):
  th = TestHarness( GcdUnitRTL() )

  th.set_param("top.src.construct",
    msgs=test_params.msgs[::2],
    initial_delay=test_params.src_delay,
    interval_delay=test_params.src_delay )

  th.set_param("top.sink.construct",
    msgs=test_params.msgs[1::2],
    initial_delay=test_params.sink_delay,
    interval_delay=test_params.sink_delay )

  run_sim( th, cmdline_opts, duts=['gcd'] )
