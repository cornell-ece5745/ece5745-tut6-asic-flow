#=========================================================================
# GCD Unit CL Model
#=========================================================================

from pymtl3      import *
from pymtl3.stdlib import stream

from .GcdUnitMsg import GcdUnitMsgs

#-------------------------------------------------------------------------
# gcd
#-------------------------------------------------------------------------
# Helper function that uses Euclid's algorithm to calculate the greatest
# common denomiator, but also to estimate the number of cycles a simple
# FSM-based GCD unit might take.

def gcd_cl( a, b ):
  ncycles = 0
  while True:
    ncycles += 1
    if a < b:
      a,b = b,a
    elif b != 0:
      a = a - b
    else:
      return (a,ncycles)

#-------------------------------------------------------------------------
# GcdUnitCL
#-------------------------------------------------------------------------

class GcdUnitCL( Component ):

  # Constructor

  def construct( s ):

    # Interface

    s.recv = stream.ifcs.RecvIfcRTL(GcdUnitMsgs.req)
    s.send = stream.ifcs.SendIfcRTL(GcdUnitMsgs.resp)

    # Queues

    s.req_q  = stream.RecvQueueAdapter(GcdUnitMsgs.req) # gives a deq method to call
    s.resp_q = stream.SendQueueAdapter(GcdUnitMsgs.resp) # gives a send method to call

    s.recv //= s.req_q.recv
    s.send //= s.resp_q.send

    # Member variables

    s.result  = None
    s.counter = 0

    # CL block

    @update_once
    def block():

      if s.result is not None:
        # Handle delay to model the gcd unit latency
        if s.counter > 0:
          s.counter -= 1
        elif s.resp_q.enq.rdy():
          s.resp_q.enq( s.result )
          s.result = None

      elif s.req_q.deq.rdy():
        msg = s.req_q.deq()
        s.result, s.counter = gcd_cl(msg.a, msg.b)

  # Line tracing

  def line_trace( s ):
    return f"{s.recv}({s.counter:^4}){s.send}"
