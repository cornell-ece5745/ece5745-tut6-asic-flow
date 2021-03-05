#=========================================================================
# MinMaxUnit_test
#=========================================================================

import pytest

from random             import randint

from pymtl3             import *
from pymtl3.stdlib.test_utils import run_test_vector_sim
from ..MinMaxUnit        import MinMaxUnit

#-------------------------------------------------------------------------
# test_basic
#-------------------------------------------------------------------------

def test_basic( cmdline_opts ):
  run_test_vector_sim( MinMaxUnit(Bits8), [
    ('in0   in1   out_min* out_max*'),
    [ 0x00, 0x00, 0x00,    0x00     ],
    [ 0x04, 0x03, 0x03,    0x04     ],
    [ 0x09, 0x06, 0x06,    0x09     ],
    [ 0x0a, 0x0f, 0x0a,    0x0f     ],
    [ 0xff, 0x10, 0x10,    0xff     ],
  ], cmdline_opts )

#-------------------------------------------------------------------------
# test_random
#-------------------------------------------------------------------------

@pytest.mark.parametrize( "nbits", [ 4, 8, 16, 32 ] )
def test_random( nbits, cmdline_opts ):

  test_vector_table = [( 'in0', 'in1', 'out_min*', 'out_max*' )]
  for i in range(20):
    in0 = randint(0,2**nbits-1)
    in1 = randint(0,2**nbits-1)
    test_vector_table.append( [ in0, in1, min(in0,in1), max(in0,in1) ] )

  run_test_vector_sim( MinMaxUnit( nbits ), test_vector_table, cmdline_opts )
