#=========================================================================
# GcdUnitMsg
#=========================================================================

from pymtl3 import *

#-------------------------------------------------------------------------
# GcdUnitReqMsg
#-------------------------------------------------------------------------
# BitStruct designed to hold two operands for a multiply

@bitstruct
class GcdUnitReqMsg:
  a: Bits16
  b: Bits16

class GcdUnitMsgs:
  req  = GcdUnitReqMsg
  resp = Bits16
