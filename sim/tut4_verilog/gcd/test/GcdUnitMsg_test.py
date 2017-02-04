#=========================================================================
# GcdUnitMsg_test
#=========================================================================
# Test suite for the GCD unit message

from pymtl                       import *
from tut4_verilog.gcd.GcdUnitMsg import GcdUnitReqMsg

#-------------------------------------------------------------------------
# test_fields
#-------------------------------------------------------------------------

def test_fields():

  # Create msg

  msg = GcdUnitReqMsg()
  msg.a = 1
  msg.b = 2

  # Verify msg

  assert msg.a == 1
  assert msg.b == 2

#-------------------------------------------------------------------------
# test_mk_msg
#-------------------------------------------------------------------------

def test_mk_msg():

  # Create msg

  msg = GcdUnitReqMsg().mk_msg( 1, 2 )

  # Verify msg

  assert msg.a == 1
  assert msg.b == 2

#-------------------------------------------------------------------------
# test_str
#-------------------------------------------------------------------------

def test_str():

  # Create msg

  msg = GcdUnitReqMsg()
  msg.a = 0xdead
  msg.b = 0xbeef

  # Verify string

  assert str(msg) == "dead:beef"

