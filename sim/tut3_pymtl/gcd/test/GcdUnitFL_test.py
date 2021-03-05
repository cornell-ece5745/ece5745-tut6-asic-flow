#=========================================================================
# GcdUnitFL_test
#=========================================================================

import pytest
import random

from math  import gcd

from pymtl3  import *
from pymtl3.stdlib.test_utils import mk_test_case_table

from tut3_pymtl.gcd.GcdUnitFL  import gcd_fl

# To ensure reproducible testing

random.seed(0xdeadbeef)

def test_gcd_fl():
  #           a   b         result
  assert gcd_fl( 0,  0  ) == ( 0      )
  assert gcd_fl( 1,  0  ) == ( 1      )
  assert gcd_fl( 0,  1  ) == ( 1      )
  assert gcd_fl( 5,  5  ) == ( 5      )
  assert gcd_fl( 15, 5  ) == ( 5      )
  assert gcd_fl( 5,  15 ) == ( 5      )
  assert gcd_fl( 7,  13 ) == ( 1      )
  assert gcd_fl( 75, 45 ) == ( 15    )
  assert gcd_fl( 36, 96 ) == ( 12    )

#-------------------------------------------------------------------------
# Test cases
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

#-------------------------------------------------------------------------
# Test Case: random
#-------------------------------------------------------------------------

random_cases = []
for i in range(30):
  a = random.randint(0,0xffff)
  b = random.randint(0,0xffff)
  c = gcd( a, b )
  random_cases.append( ( a, b, c ) )

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (           "cases      "),
  [ "basic",  basic_cases, ],
  [ "random", random_cases ],
])

@pytest.mark.parametrize( **test_case_table )
def test_gcd_fl( test_params ):
  print()
  for a, b, result in test_params.cases:
    print(f"gcd_fl({b16(a)}, {b16(b)}) = {gcd_fl(b16(a), b16(b))} (ref = {b16(result)})")
    assert gcd_fl(b16(a), b16(b)) == b16(result)
