#=========================================================================
# Regincr2stage_test
#=========================================================================

import random

from pymtl3 import *
from pymtl3.stdlib.test_utils import run_test_vector_sim
from ..RegIncr2stage import RegIncr2stage

#-------------------------------------------------------------------------
# test_small
#-------------------------------------------------------------------------

def test_small( cmdline_opts ):
  run_test_vector_sim( RegIncr2stage(), [
    ('in_   out*'),
    [ 0x00, '?'  ],
    [ 0x03, '?'  ],
    [ 0x06, 0x02 ],
    [ 0x00, 0x05 ],
    [ 0x00, 0x08 ],
  ], cmdline_opts )

#-------------------------------------------------------------------------
# test_large
#-------------------------------------------------------------------------

def test_large( cmdline_opts ):
  run_test_vector_sim( RegIncr2stage(), [
    ('in_   out*'),
    [ 0xa0, '?'  ],
    [ 0xb3, '?'  ],
    [ 0xc6, 0xa2 ],
    [ 0x00, 0xb5 ],
    [ 0x00, 0xc8 ],
  ], cmdline_opts )

#-------------------------------------------------------------------------
# test_overflow
#-------------------------------------------------------------------------

def test_overflow( cmdline_opts ):
  run_test_vector_sim( RegIncr2stage(), [
    ('in_   out*'),
    [ 0x00, '?'  ],
    [ 0xfe, '?'  ],
    [ 0xff, 0x02 ],
    [ 0x00, 0x00 ],
    [ 0x00, 0x01 ],
  ], cmdline_opts )

#-------------------------------------------------------------------------
# test_random
#-------------------------------------------------------------------------

def test_random( cmdline_opts ):

  test_vector_table = [( 'in_', 'out*' )]
  last_result_0 = '?'
  last_result_1 = '?'
  for i in range(20):
    rand_value = b8( random.randint(0,0xff) )
    test_vector_table.append( [ rand_value, last_result_1 ] )
    last_result_1 = last_result_0
    last_result_0 = b8( rand_value + 2, trunc_int=True )

  run_test_vector_sim( RegIncr2stage(), test_vector_table, cmdline_opts )
