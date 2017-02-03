#=========================================================================
# Sort Unit CL Model
#=========================================================================
# Models the cycle-approximate timing behavior of the target hardware.

from collections import deque
from copy        import deepcopy

from pymtl       import *

class SortUnitCL( Model ):

  # Constructor

  def __init__( s, nbits=8, nstages=3 ):

    s.in_val  = InPort (1)
    s.in_     = [ InPort  (nbits) for _ in range(4) ]

    s.out_val = OutPort(1)
    s.out     = [ OutPort (nbits) for _ in range(4) ]

    s.pipe    = deque( [[0,0,0,0,0]]*(nstages-1) )

    @s.tick_cl
    def block():
      s.pipe.append( deepcopy( [s.in_val] + sorted(s.in_) ) )
      data = s.pipe.popleft()
      s.out_val.next = data[0]
      for i, v in enumerate( data[1:] ):
        s.out[i].next = v

  # Line tracing

  def line_trace( s ):

    in_str = '{' + ','.join(map(str,s.in_)) + '}'
    if not s.in_val:
      in_str = ' '*len(in_str)

    out_str = '{' + ','.join(map(str,s.out)) + '}'
    if not s.out_val:
      out_str = ' '*len(out_str)

    return "{}|{}".format( in_str, out_str )

