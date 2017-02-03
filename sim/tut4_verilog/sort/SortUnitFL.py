#=========================================================================
# Sort Unit FL Model
#=========================================================================
# Models the functional behavior of the target hardware but not the
# timing.

from pymtl      import *

class SortUnitFL( Model ):

  # Constructor

  def __init__( s, nbits=8 ):

    s.in_val  = InPort(1)
    s.in_     = [ InPort  (nbits) for x in range(4) ]

    s.out_val = OutPort(1)
    s.out     = [ OutPort (nbits) for x in range(4) ]

    @s.tick_fl
    def block():
      s.out_val.next = s.in_val
      for i, v in enumerate( sorted( s.in_ ) ):
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

