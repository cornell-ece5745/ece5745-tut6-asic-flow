#=========================================================================
# Sort Unit FL Model
#=========================================================================
# Models the functional behavior of the target hardware but not the
# timing.

from pymtl3 import *
from copy   import deepcopy

def sort_fl( arr ):
  def sort( a, l, r ):
    i, j = l, r;
    x = a[ (l+r) >> 1 ]
    while i <= j:
      while a[i] < x: i += 1
      while a[j] > x: j -= 1
      if i <= j:
        a[i], a[j]= a[j], a[i]
        i += 1
        j -= 1
    if l < j: sort( a, l, j )
    if i < r: sort( a, i, r )

  ret = deepcopy(arr)
  sort( ret, 0, len(ret)-1 )
  return ret

