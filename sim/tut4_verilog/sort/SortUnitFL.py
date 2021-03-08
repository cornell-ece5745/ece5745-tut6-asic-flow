#=========================================================================
# Sort Unit FL Model
#=========================================================================
# Models the functional behavior of the target hardware but not the
# timing.

from copy import deepcopy
from pymtl3 import *

def sort_fl( arr ):
  def sort( a, l, r ):
    i, j = l, r;
    x = a[ (l+r) >> 1 ]
    while i <= j:
      while a[i] < x: i += 1
      while a[j] > x: j -= 1
      if i <= j:
        a[i], a[j] = a[j], a[i]
        i += 1
        j -= 1
    if l < j: sort( a, l, j )
    if i < r: sort( a, i, r )

  ret = arr[::]
  sort( ret, 0, len(ret)-1 )
  return ret

class SortUnitFL( Component ):

  # Constructor

  def construct( s, nbits=8 ):

    s.in_val = InPort ()
    s.in_    = [ InPort (nbits) for _ in range(4) ]

    s.out_val = OutPort()
    s.out     = [ OutPort(nbits) for _ in range(4) ]

    @update_ff
    def block():
      s.out_val <<= s.in_val
      for i, v in enumerate( sort_fl( s.in_ ) ):
        s.out[i] <<= v

  # Line tracing

  def line_trace( s ):

    in_str = '{' + ','.join(map(str,s.in_)) + '}'
    if not s.in_val:
      in_str = ' '*len(in_str)

    out_str = '{' + ','.join(map(str,s.out)) + '}'
    if not s.out_val:
      out_str = ' '*len(out_str)

    return f"{in_str}|{out_str}"
