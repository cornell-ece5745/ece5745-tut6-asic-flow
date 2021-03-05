#=========================================================================
# GcdUnitMsg_test
#=========================================================================
# Test suite for the GCD unit message

from pymtl3                    import *
from tut3_pymtl.gcd.GcdUnitMsg import GcdUnitReqMsg

#-------------------------------------------------------------------------
# test_fields
#-------------------------------------------------------------------------

def test_fields():

  # Create msg

  msg = GcdUnitReqMsg()
  msg.a = b16(1)
  msg.b = b16(2)

  # Verify msg

  assert msg.a == 1
  assert msg.b == 2

#-------------------------------------------------------------------------
# test_mk_msg
#-------------------------------------------------------------------------

def test_mk_msg():

  # Create msg

  msg = GcdUnitReqMsg(1,2)

  # Verify msg

  assert msg.a == 1
  assert msg.b == 2

#-------------------------------------------------------------------------
# test_str
#-------------------------------------------------------------------------

def test_str():

  # Create msg

  msg = GcdUnitReqMsg(0xdead, 0xbeef)

  # Verify string

  assert str(msg) == "dead:beef"

