#=========================================================================
# GCD Unit FL Model
#=========================================================================

from math import gcd

from pymtl3 import *
from pymtl3.stdlib import stream

from .GcdUnitMsg import GcdUnitMsgs

#-------------------------------------------------------------------------
# GcdUnitFL
#-------------------------------------------------------------------------

class GcdUnitFL( Component ):

  # Constructor

  def construct( s ):

    # Interface

    s.recv = stream.ifcs.RecvIfcRTL(GcdUnitMsgs.req)
    s.send = stream.ifcs.SendIfcRTL(GcdUnitMsgs.resp)

    # Queue Adapters

    s.req_q  = stream.RecvQueueAdapter(GcdUnitMsgs.req) # gives a deq method to call
    s.resp_q = stream.SendQueueAdapter(GcdUnitMsgs.resp) # gives a send method to call

    s.recv //= s.req_q.recv
    s.send //= s.resp_q.send

    # FL block

    @update_once
    def block():
      if s.resp_q.enq.rdy() and s.req_q.deq.rdy():
        msg = s.req_q.deq()
        s.resp_q.enq( gcd(msg.a, msg.b) )

  # Line tracing

  def line_trace( s ):
    return f"{s.recv}(){s.send}"
