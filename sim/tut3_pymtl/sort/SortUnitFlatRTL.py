#=========================================================================
# SortUnitFlatRTL
#=========================================================================
# A register-transfer-level model explicitly represents state elements
# with s.tick concurrent blocks and uses s.combinational concurrent
# blocks to model how data transfers between state elements.

from pymtl3 import *

class SortUnitFlatRTL( Component ):

  #=======================================================================
  # Constructor
  #=======================================================================

  def construct( s, nbits=8 ):

    #---------------------------------------------------------------------
    # Interface
    #---------------------------------------------------------------------

    s.in_val  = InPort ()
    s.in_     = [ InPort (nbits) for _ in range(4) ]

    s.out_val = OutPort()
    s.out     = [ OutPort(nbits) for _ in range(4) ]

    #---------------------------------------------------------------------
    # Stage S0->S1 pipeline registers
    #---------------------------------------------------------------------

    s.val_S1 = Wire()
    s.elm_S1 = [ Wire(nbits) for _ in range(4) ]

    @update_ff
    def pipereg_S0S1():

      if s.reset:
        s.val_S1 <<= 0
      else:
        s.val_S1 <<= s.in_val

      for i in range(4):
        s.elm_S1[i] <<= s.in_[i]

    #---------------------------------------------------------------------
    # Stage S1 combinational logic
    #---------------------------------------------------------------------

    s.elm_next_S1 = [ Wire(nbits) for _ in range(4) ]

    @update
    def stage_S1():

      # Sort elements 0 and 1

      if s.elm_S1[0] <= s.elm_S1[1]:
        s.elm_next_S1[0] @= s.elm_S1[0]
        s.elm_next_S1[1] @= s.elm_S1[1]
      else:
        s.elm_next_S1[0] @= s.elm_S1[1]
        s.elm_next_S1[1] @= s.elm_S1[0]

      # Sort elements 2 and 3

      if s.elm_S1[2] <= s.elm_S1[3]:
        s.elm_next_S1[2] @= s.elm_S1[2]
        s.elm_next_S1[3] @= s.elm_S1[3]
      else:
        s.elm_next_S1[2] @= s.elm_S1[3]
        s.elm_next_S1[3] @= s.elm_S1[2]

    #---------------------------------------------------------------------
    # Stage S1->S2 pipeline registers
    #---------------------------------------------------------------------

    s.val_S2 = Wire()
    s.elm_S2 = [ Wire(nbits) for _ in range(4) ]

    @update_ff
    def pipereg_S1S2():
      if s.reset:
        s.val_S2 <<= 0
      else:
        s.val_S2 <<= s.val_S1

      for i in range(4):
        s.elm_S2[i] <<= s.elm_next_S1[i]

    #----------------------------------------------------------------------
    # Stage S2 combinational logic
    #----------------------------------------------------------------------

    s.elm_next_S2 = [ Wire(nbits) for _ in range(4) ]

    @update
    def stage_S2():

      # Sort elements 0 and 2

      if s.elm_S2[0] <= s.elm_S2[2]:
        s.elm_next_S2[0] @= s.elm_S2[0]
        s.elm_next_S2[2] @= s.elm_S2[2]
      else:
        s.elm_next_S2[0] @= s.elm_S2[2]
        s.elm_next_S2[2] @= s.elm_S2[0]

      # Sort elements 1 and 3

      if s.elm_S2[1] <= s.elm_S2[3]:
        s.elm_next_S2[1] @= s.elm_S2[1]
        s.elm_next_S2[3] @= s.elm_S2[3]
      else:
        s.elm_next_S2[1] @= s.elm_S2[3]
        s.elm_next_S2[3] @= s.elm_S2[1]

    #----------------------------------------------------------------------
    # Stage S2->S3 pipeline registers
    #----------------------------------------------------------------------

    s.val_S3 = Wire()
    s.elm_S3 = [ Wire(nbits) for _ in range(4) ]

    @update_ff
    def pipereg_S2S3():
      if s.reset:
        s.val_S3 <<= 0
      else:
        s.val_S3 <<= s.val_S2

      for i in range(4):
        s.elm_S3[i] <<= s.elm_next_S2[i]

    #----------------------------------------------------------------------
    # Stage S3 combinational logic
    #----------------------------------------------------------------------

    s.elm_next_S3 = [ Wire(nbits) for _ in range(4) ]

    @update
    def stage_S3():

      # Pass through elements 0 and 3

      s.elm_next_S3[0] @= s.elm_S3[0]
      s.elm_next_S3[3] @= s.elm_S3[3]

      # Sort elements 1 and 2

      if s.elm_S3[1] <= s.elm_S3[2]:
        s.elm_next_S3[1] @= s.elm_S3[1]
        s.elm_next_S3[2] @= s.elm_S3[2]
      else:
        s.elm_next_S3[1] @= s.elm_S3[2]
        s.elm_next_S3[2] @= s.elm_S3[1]

    # Assign output ports

    s.out_val //= s.val_S3

    @update
    def comb_logic():
      for i in range(4):
        s.out[i] @= s.elm_next_S3[i] & (sext(s.out_val, nbits))

  #=======================================================================
  # Line tracing
  #=======================================================================

  def line_trace( s ):

    def trace_val_elm( val, elm ):
      str_ = f'{{{elm[0]},{elm[1]},{elm[2]},{elm[3]}}}'
      if not val:
        str_ = ' '*len(str_)
      return str_

    return "{}|{}|{}|{}|{}".format(
      trace_val_elm( s.in_val,  s.in_    ),
      trace_val_elm( s.val_S1,  s.elm_S1 ),
      trace_val_elm( s.val_S2,  s.elm_S2 ),
      trace_val_elm( s.val_S3,  s.elm_S3 ),
      trace_val_elm( s.out_val, s.out    ),
    )

