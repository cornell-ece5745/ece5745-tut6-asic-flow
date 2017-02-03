#=========================================================================
# SortUnitFlatRTL_v_test
#=========================================================================

from pymtl           import *
from SortUnitFlatRTL import SortUnitFlatRTL

def test_verilate( dump_vcd, test_verilog ):

  # Conflat the model

  model = SortUnitFlatRTL()
  model.vcd_file = dump_vcd

  # Translate the model into Verilog

  if test_verilog:
    model = TranslationTool( model )

  # Elaborate the model

  model.elaborate()

  # Create and reset simulator

  sim = SimulationTool( model )
  sim.reset()
  print ""

  # Helper function

  def t( in_val, in_, out_val, out ):

    model.in_val.value = in_val
    for i,v in enumerate( in_ ):
      model.in_[i].value = v

    sim.eval_combinational()
    sim.print_line_trace()

    assert model.out_val == out_val
    if ( out_val ):
      for i,v in enumerate( out ):
        assert model.out[i] == v

    sim.cycle()

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

