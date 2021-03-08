#=========================================================================
# GcdUnitFL_test
#=========================================================================

import pytest
import random

from math  import gcd

from pymtl3  import *
from pymtl3.stdlib.test_utils import mk_test_case_table, run_sim

from pymtl3.stdlib import stream
from tut3_pymtl.gcd.GcdUnitFL  import GcdUnitFL
from tut3_pymtl.gcd.GcdUnitMsg import GcdUnitMsgs

# To ensure reproducible testing

random.seed(0xdeadbeef)

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

basic_cases = [
  ( 15,     5     , 5    ),
  ( 3,      9     , 3    ),
  ( 0,      0     , 0    ),
  ( 27,     15    , 3    ),
  ( 21,     49    , 7    ),
  ( 25,     30    , 5    ),
  ( 19,     27    , 1    ),
  ( 40,     40    , 40   ),
  ( 250,    190   , 10   ),
  ( 5,      250   , 5    ),
  ( 0xffff, 0x00ff, 0xff ),
]

basic_msgs = []
for a, b, result in basic_cases:
  basic_msgs.extend( [GcdUnitMsgs.req(a, b), GcdUnitMsgs.resp( result )] )

#-------------------------------------------------------------------------
# Test Case: random
#-------------------------------------------------------------------------

random_cases = []
for i in range(30):
  a = random.randint(0,0xffff)
  b = random.randint(0,0xffff)
  c = gcd( a, b )
  random_cases.append( ( a, b, c ) )

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
def test_gcd_fl( test_params ):

  th = TestHarness( GcdUnitFL() )

  th.set_param("top.src.construct",
    msgs=test_params.msgs[::2],
    initial_delay=test_params.src_delay,
    interval_delay=test_params.src_delay )

  th.set_param("top.sink.construct",
    msgs=test_params.msgs[1::2],
    initial_delay=test_params.sink_delay,
    interval_delay=test_params.sink_delay )

  run_sim( th )
