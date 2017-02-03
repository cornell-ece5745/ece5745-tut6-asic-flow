#=========================================================================
# SortUnitFlatRTL
#=========================================================================
# A register-transfer-level model explicitly represents state elements
# with s.tick concurrent blocks and uses s.combinational concurrent
# blocks to model how data transfers between state elements.

from pymtl import *

class SortUnitFlatRTL( Model ):

  #=======================================================================
  # Constructor
  #=======================================================================

  def __init__( s, nbits=8 ):

    #---------------------------------------------------------------------
    # Interface
    #---------------------------------------------------------------------

    s.in_val  = InPort (1)
    s.in_     = [ InPort  (nbits) for _ in range(4) ]

    s.out_val = OutPort(1)
    s.out     = [ OutPort (nbits) for _ in range(4) ]

    #---------------------------------------------------------------------
    # Stage S0->S1 pipeline registers
    #---------------------------------------------------------------------

    s.val_S1 = Wire(1)
    s.elm_S1 = [ Wire(nbits) for _ in range(4) ]

    @s.tick_rtl
    def pipereg_S0S1():
      s.val_S1.next  = s.in_val if ~s.reset else 0
      for i in xrange(4):
        s.elm_S1[i].next = s.in_[i]

    #---------------------------------------------------------------------
    # Stage S1 combinational logic
    #---------------------------------------------------------------------

    s.elm_next_S1 = [ Wire(nbits) for _ in range(4) ]

    @s.combinational
    def stage_S1():

      # Sort elements 0 and 1

      if s.elm_S1[0] <= s.elm_S1[1]:
        s.elm_next_S1[0].value = s.elm_S1[0]
        s.elm_next_S1[1].value = s.elm_S1[1]
      else:
        s.elm_next_S1[0].value = s.elm_S1[1]
        s.elm_next_S1[1].value = s.elm_S1[0]

      # Sort elements 2 and 3

      if s.elm_S1[2] <= s.elm_S1[3]:
        s.elm_next_S1[2].value = s.elm_S1[2]
        s.elm_next_S1[3].value = s.elm_S1[3]
      else:
        s.elm_next_S1[2].value = s.elm_S1[3]
        s.elm_next_S1[3].value = s.elm_S1[2]

    #---------------------------------------------------------------------
    # Stage S1->S2 pipeline registers
    #---------------------------------------------------------------------

    s.val_S2 = Wire(1)
    s.elm_S2 = [ Wire(nbits) for _ in range(4) ]

    @s.tick_rtl
    def pipereg_S1S2():
      s.val_S2.next  = s.val_S1 if ~s.reset else 0
      for i in xrange(4):
        s.elm_S2[i].next = s.elm_next_S1[i]

    #----------------------------------------------------------------------
    # Stage S2 combinational logic
    #----------------------------------------------------------------------

    s.elm_next_S2 = [ Wire(nbits) for _ in range(4) ]

    @s.combinational
    def stage_S2():

      # Sort elements 0 and 2

      if s.elm_S2[0] <= s.elm_S2[2]:
        s.elm_next_S2[0].value = s.elm_S2[0]
        s.elm_next_S2[2].value = s.elm_S2[2]
      else:
        s.elm_next_S2[0].value = s.elm_S2[2]
        s.elm_next_S2[2].value = s.elm_S2[0]

      # Sort elements 1 and 3

      if s.elm_S2[1] <= s.elm_S2[3]:
        s.elm_next_S2[1].value = s.elm_S2[1]
        s.elm_next_S2[3].value = s.elm_S2[3]
      else:
        s.elm_next_S2[1].value = s.elm_S2[3]
        s.elm_next_S2[3].value = s.elm_S2[1]

    #----------------------------------------------------------------------
    # Stage S2->S3 pipeline registers
    #----------------------------------------------------------------------

    s.val_S3 = Wire(1)
    s.elm_S3 = [ Wire(nbits) for _ in range(4) ]

    @s.tick_rtl
    def pipereg_S2S3():
      s.val_S3.next  = s.val_S2 if ~s.reset else 0
      for i in xrange(4):
        s.elm_S3[i].next = s.elm_next_S2[i]

    #----------------------------------------------------------------------
    # Stage S3 combinational logic
    #----------------------------------------------------------------------

    s.elm_next_S3 = [ Wire(nbits) for _ in range(4) ]

    @s.combinational
    def stage_S3():

      # Pass through elements 0 and 3

      s.elm_next_S3[0].value = s.elm_S3[0]
      s.elm_next_S3[3].value = s.elm_S3[3]

      # Sort elements 1 and 2

      if s.elm_S3[1] <= s.elm_S3[2]:
        s.elm_next_S3[1].value = s.elm_S3[1]
        s.elm_next_S3[2].value = s.elm_S3[2]
      else:
        s.elm_next_S3[1].value = s.elm_S3[2]
        s.elm_next_S3[2].value = s.elm_S3[1]

    # Assign output ports

    s.connect( s.out_val, s.val_S3 )
    for i in xrange(4):
      s.connect( s.out[i], s.elm_next_S3[i] )

  #=======================================================================
  # Line tracing
  #=======================================================================

  def line_trace( s ):

    def trace_val_elm( val, elm ):
      str_ = '{{{},{},{},{}}}'.format( elm[0], elm[1], elm[2], elm[3] )
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

