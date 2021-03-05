#=========================================================================
# SortUnitFL_test
#=========================================================================

from random     import randint

from pymtl3 import *
from ..SortUnitFL  import sort_fl


#-------------------------------------------------------------------------
# test_random
#-------------------------------------------------------------------------

tvec_stream = [ [ 4, 3, 2, 1 ], [ 9, 6, 7, 1 ], [ 4, 8, 0, 9 ] ]
tvec_dups   = [ [ 2, 8, 9, 9 ], [ 2, 8, 2, 8 ], [ 1, 1, 1, 1 ] ]
tvec_sorted = [ [ 1, 2, 3, 4 ], [ 1, 3, 5, 7 ], [ 4, 3, 2, 1 ] ]
tvec_random = [ [ randint(0,0xff) for _ in range(4) ] for _ in range(20) ]

def test_sort_fl_tvec_stream():
  print()
  for v in tvec_stream:
    print("input:", v, "| sort_fl:", sort_fl(v), "ref:",sorted(v))
    assert sort_fl( v ) == sorted( v )

def test_sort_fl_tvec_dups():
  print()
  for v in tvec_dups:
    print("input:", v, "| sort_fl:", sort_fl(v), "ref:",sorted(v))
    assert sort_fl( v ) == sorted( v )

def test_sort_fl_tvec_sorted():
  print()
  for v in tvec_stream:
    print("input:", v, "| sort_fl:", sort_fl(v), "ref:",sorted(v))
    assert sort_fl( v ) == sorted( v )

def test_sort_fl_tvec_random():
  print()
  for v in tvec_random:
    print("input:", v, "| sort_fl:", sort_fl(v), "ref:",sorted(v))
    assert sort_fl( v ) == sorted( v )
