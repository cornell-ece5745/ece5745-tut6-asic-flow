#=========================================================================
# SortUnitFlatRTL_v_test
#=========================================================================

from pymtl3                         import *
from pymtl3.passes.backends.verilog import *
from pymtl3.stdlib.test_utils       import config_model_with_cmdline_opts
from ..SortUnitFlatRTL               import SortUnitFlatRTL

def test_verilate( cmdline_opts ):

  # Conflat the model

  model = SortUnitFlatRTL(8)

  # Configure the model

  model = config_model_with_cmdline_opts( model, cmdline_opts, duts=[] ) # use model itself

  # Create and reset simulator

  model.apply( DefaultPassGroup(linetrace=True) )
  model.sim_reset()

  # Helper function

  def t( in_val, in_, out_val, out ):

    model.in_val @= in_val
    for i,v in enumerate( in_ ):
      model.in_[i] @= v

    model.sim_eval_combinational()

    assert model.out_val == out_val
    if ( out_val ):
      for i,v in enumerate( out ):
        assert model.out[i] == v

    model.sim_tick()

  # Cycle-by-cycle tests

  t( 0, [ 0x00, 0x00, 0x00, 0x00 ], 0, [ 0x00, 0x00, 0x00, 0x00 ] )
  t( 1, [ 0x03, 0x09, 0x04, 0x01 ], 0, [ 0x00, 0x00, 0x00, 0x00 ] )
  t( 1, [ 0x10, 0x23, 0x02, 0x41 ], 0, [ 0x00, 0x00, 0x00, 0x00 ] )
  t( 1, [ 0x02, 0x55, 0x13, 0x07 ], 0, [ 0x00, 0x00, 0x00, 0x00 ] )
  t( 0, [ 0x00, 0x00, 0x00, 0x00 ], 1, [ 0x01, 0x03, 0x04, 0x09 ] )
  t( 0, [ 0x00, 0x00, 0x00, 0x00 ], 1, [ 0x02, 0x10, 0x23, 0x41 ] )
  t( 0, [ 0x00, 0x00, 0x00, 0x00 ], 1, [ 0x02, 0x07, 0x13, 0x55 ] )
  t( 0, [ 0x00, 0x00, 0x00, 0x00 ], 0, [ 0x00, 0x00, 0x00, 0x00 ] )
  t( 0, [ 0x00, 0x00, 0x00, 0x00 ], 0, [ 0x00, 0x00, 0x00, 0x00 ] )

