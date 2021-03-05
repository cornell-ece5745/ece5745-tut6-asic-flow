#=========================================================================
# GCD Unit RTL Model
#=========================================================================

from pymtl3 import *
from pymtl3.stdlib import stream
from pymtl3.stdlib.basic_rtl  import Mux, RegEn, RegRst
from pymtl3.stdlib.basic_rtl  import LTComparator, ZeroComparator, Subtractor

from .GcdUnitMsg  import GcdUnitMsgs

#=========================================================================
# Constants
#=========================================================================

A_MUX_SEL_NBITS = 2
A_MUX_SEL_IN    = 0
A_MUX_SEL_SUB   = 1
A_MUX_SEL_B     = 2
A_MUX_SEL_X     = 0

B_MUX_SEL_NBITS = 1
B_MUX_SEL_A     = 0
B_MUX_SEL_IN    = 1
B_MUX_SEL_X     = 0

#=========================================================================
# GCD Unit RTL Datapath
#=========================================================================

class GcdUnitDpathRTL(Component):

  # Constructor

  def construct( s ):

    #---------------------------------------------------------------------
    # Interface
    #---------------------------------------------------------------------

    s.req_msg_a = InPort (16)
    s.req_msg_b = InPort (16)
    s.resp_msg  = OutPort(16)

    # Control signals (ctrl -> dpath)

    s.a_mux_sel = InPort( A_MUX_SEL_NBITS )
    s.a_reg_en  = InPort()
    s.b_mux_sel = InPort( B_MUX_SEL_NBITS )
    s.b_reg_en  = InPort()

    # Status signals (dpath -> ctrl)

    s.is_b_zero = OutPort()
    s.is_a_lt_b = OutPort()

    #---------------------------------------------------------------------
    # Structural composition
    #---------------------------------------------------------------------

    # A mux

    s.sub_out   = Wire(16)
    s.b_reg_out = Wire(16)

    s.a_mux = m = Mux( Bits16, 3 )
    m.sel //= s.a_mux_sel
    m.in_[A_MUX_SEL_IN ] //= s.req_msg_a
    m.in_[A_MUX_SEL_SUB] //= s.sub_out
    m.in_[A_MUX_SEL_B  ] //= s.b_reg_out

    # A register

    s.a_reg = m = RegEn(Bits16)
    m.en  //= s.a_reg_en
    m.in_ //= s.a_mux.out

    # B mux

    s.b_mux = m = Mux( Bits16, 2 )
    m.sel //= s.b_mux_sel
    m.in_[B_MUX_SEL_A ] //= s.a_reg.out
    m.in_[B_MUX_SEL_IN] //= s.req_msg_b

    # B register

    s.b_reg = m = RegEn(Bits16)
    m.en  //= s.b_reg_en
    m.in_ //= s.b_mux.out
    m.out //= s.b_reg_out

    # Zero compare

    s.b_zero = m = ZeroComparator(Bits16)
    m.in_ //= s.b_reg.out
    m.out //= s.is_b_zero

    # Less-than comparator

    s.a_lt_b = m = LTComparator(Bits16)
    m.in0 //= s.a_reg.out
    m.in1 //= s.b_reg.out
    m.out //= s.is_a_lt_b

    # Subtractor

    s.sub = m = Subtractor(Bits16)
    m.in0 //= s.a_reg.out
    m.in1 //= s.b_reg.out
    m.out //= s.sub_out

    # connect to output port

    s.resp_msg //= s.sub.out

#=========================================================================
# GCD Unit RTL Control
#=========================================================================

class GcdUnitCtrlRTL(Component):

  def construct( s ):

    #---------------------------------------------------------------------
    # Interface
    #---------------------------------------------------------------------

    s.req_val   = InPort ()
    s.req_rdy   = OutPort()

    s.resp_val  = OutPort()
    s.resp_rdy  = InPort ()

    # Control signals (ctrl -> dpath)

    s.a_mux_sel = OutPort( A_MUX_SEL_NBITS )
    s.a_reg_en  = OutPort()
    s.b_mux_sel = OutPort()
    s.b_reg_en  = OutPort()

    # Status signals (dpath -> ctrl)

    s.is_b_zero = InPort( B_MUX_SEL_NBITS )
    s.is_a_lt_b = InPort()

    # State element

    s.STATE_IDLE = 0
    s.STATE_CALC = 1
    s.STATE_DONE = 2

    s.state = Wire(2)

    #---------------------------------------------------------------------
    # State Transition Logic
    #---------------------------------------------------------------------

    @update_ff
    def state_transitions():
      if s.reset:
        s.state <<= s.STATE_IDLE

      # Transistions out of IDLE state

      if s.state == s.STATE_IDLE:
        if s.req_val:
          s.state <<= s.STATE_CALC

      # Transistions out of CALC state

      if s.state == s.STATE_CALC:
        if ~s.is_a_lt_b & s.is_b_zero:
          s.state <<= s.STATE_DONE

      # Transistions out of DONE state

      if s.state == s.STATE_DONE:
        if s.resp_rdy:
          s.state <<= s.STATE_IDLE

    #---------------------------------------------------------------------
    # State Output Logic
    #---------------------------------------------------------------------

    s.do_swap = Wire()
    s.do_sub  = Wire()

    @update
    def state_outputs():

      s.do_swap   @= 0
      s.do_sub    @= 0
      s.req_rdy   @= 0
      s.resp_val  @= 0
      s.a_mux_sel @= 0
      s.a_reg_en  @= 0
      s.b_mux_sel @= 0
      s.b_reg_en  @= 0

      # In IDLE state we simply wait for inputs to arrive and latch them

      if s.state == s.STATE_IDLE:
        s.req_rdy   @= 1
        s.resp_val  @= 0
        s.a_mux_sel @= A_MUX_SEL_IN
        s.a_reg_en  @= 1
        s.b_mux_sel @= B_MUX_SEL_IN
        s.b_reg_en  @= 1

      # In CALC state we iteratively swap/sub to calculate GCD

      elif s.state == s.STATE_CALC:

        s.do_swap @= s.is_a_lt_b
        s.do_sub  @= ~s.is_b_zero

        s.req_rdy   @= 0
        s.resp_val  @= 0
        s.a_mux_sel @= A_MUX_SEL_B if s.do_swap else A_MUX_SEL_SUB
        s.a_reg_en  @= 1
        s.b_mux_sel @= B_MUX_SEL_A
        s.b_reg_en  @= s.do_swap

      # In DONE state we simply wait for output transaction to occur

      elif s.state == s.STATE_DONE:
        s.req_rdy   @= 0
        s.resp_val  @= 1
        s.a_mux_sel @= A_MUX_SEL_X
        s.a_reg_en  @= 0
        s.b_mux_sel @= B_MUX_SEL_X
        s.b_reg_en  @= 0

#=========================================================================
# GCD Unit RTL Model
#=========================================================================

class GcdUnitRTL( Component ):

  # Constructor

  def construct( s ):

    # Interface

    s.recv = stream.ifcs.RecvIfcRTL( GcdUnitMsgs.req )
    s.send = stream.ifcs.SendIfcRTL( GcdUnitMsgs.resp )

    # Instantiate datapath and control

    s.dpath = GcdUnitDpathRTL()
    s.ctrl  = GcdUnitCtrlRTL()

    s.dpath.req_msg_a //= s.recv.msg.a
    s.dpath.req_msg_b //= s.recv.msg.b
    s.dpath.resp_msg  //= s.send.msg
    s.ctrl.req_val  //= s.recv.val
    s.ctrl.req_rdy  //= s.recv.rdy
    s.ctrl.resp_val //= s.send.val
    s.ctrl.resp_rdy //= s.send.rdy

    # Connect status/control signals
    s.ctrl.a_mux_sel //= s.dpath.a_mux_sel
    s.ctrl.a_reg_en  //= s.dpath.a_reg_en
    s.ctrl.b_mux_sel //= s.dpath.b_mux_sel
    s.ctrl.b_reg_en  //= s.dpath.b_reg_en

    # Status signals (dpath -> ctrl)

    s.ctrl.is_b_zero //= s.dpath.is_b_zero
    s.ctrl.is_a_lt_b //= s.dpath.is_a_lt_b

  # Line tracing

  def line_trace( s ):

    state_str = "? "
    if s.ctrl.state == s.ctrl.STATE_IDLE:
      state_str = "I "
    if s.ctrl.state == s.ctrl.STATE_CALC:
      if s.ctrl.do_swap:
        state_str = "Cs"
      elif s.ctrl.do_sub:
        state_str = "C-"
      else:
        state_str = "C "
    if s.ctrl.state == s.ctrl.STATE_DONE:
      state_str = "D "

    return f"{s.recv}({s.dpath.a_reg.out} " \
           f"{s.dpath.b_reg.out} {state_str}){s.send}"
