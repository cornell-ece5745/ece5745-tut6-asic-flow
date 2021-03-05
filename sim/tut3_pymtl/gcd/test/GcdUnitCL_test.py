#=========================================================================
# GcdUnitCL_test
#=========================================================================

import pytest

from pymtl3 import *
from pymtl3.stdlib import stream
from pymtl3.stdlib.test_utils import mk_test_case_table, run_sim

from tut3_pymtl.gcd.GcdUnitCL import gcd_cl, GcdUnitCL
from tut3_pymtl.gcd.GcdUnitMsg import GcdUnitMsgs

# Reuse cases from FL tests

from .GcdUnitFL_test import basic_cases, random_cases

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
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, gcd ):

    # Instantiate models

    s.src  = stream.SourceRTL( GcdUnitMsgs.req )
    s.sink = stream.SinkRTL( GcdUnitMsgs.resp )
    s.gcd = gcd

    # Connect

    s.src.send //= s.gcd.recv
    s.gcd.send //= s.sink.recv

  def done( s ):
    return s.src.done() and s.sink.done()

  def line_trace( s ):
    return s.src.line_trace() + " > " + s.gcd.line_trace() + " > " + s.sink.line_trace()

#-------------------------------------------------------------------------
# Test Case: basic
#-------------------------------------------------------------------------

basic_msgs = []
for a, b, result in basic_cases:
  basic_msgs.extend( [GcdUnitMsgs.req(a, b), GcdUnitMsgs.resp( result )] )

#-------------------------------------------------------------------------
# Test Case: random
#-------------------------------------------------------------------------

random_msgs = []
for a, b, result in random_cases:
  random_msgs.extend( [GcdUnitMsgs.req(a, b), GcdUnitMsgs.resp( result )] )

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (               "msgs        src_delay  sink_delay"),
  [ "basic_0x0",  basic_msgs,  0,         0,         ],
  [ "basic_5x0",  basic_msgs,  5,         0,         ],
  [ "basic_0x5",  basic_msgs,  0,         5,         ],
  [ "basic_3x9",  basic_msgs,  3,         9,         ],
  [ "random_3x9", random_msgs, 3,         9,         ],
])
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
