#=========================================================================
# flow_tut6_sort.py
#=========================================================================

import os
from prefect import Flow
from pyhflow.steps.adk import ADK
from pyhflow.steps.block import Block
from pyhflow.steps.snps_dc_synthesis import Synthesis
from pyhflow.steps.snps_vcd2saif import Vcd2Saif
from pyhflow.steps.cdns_innovus_pnr import PlaceAndRoute
from pyhflow.steps.snps_pt_pwr import PowerAnalysis
from pyhflow.steps.summary import Summary

adk_dir    = os.environ['ADK_PKGS']
adk_config = f'{adk_dir}/freepdk-45nm/stdview/adk-stdview.yml'

#-------------------------------------------------------------------------
# Flow parameters
#-------------------------------------------------------------------------

build_dir = '../../../sim/build'
files = [
  f'{build_dir}/SortUnitStructRTL__nbits_8__pickled.v',
  f'{build_dir}/sort-rtl-struct-random.verilator1.vcd',
]
top_name   = 'SortUnitStructRTL__nbits_8'
clk_period = 1.0 #ns

#-------------------------------------------------------------------------
# Instantiate step instances
#-------------------------------------------------------------------------

block    = Block( files, top_name, clk_period=clk_period, name='block' )
getadk   = ADK( adk_config, name='adk' )
vcd2saif = Vcd2Saif( name='vcd2saif' )
synth    = Synthesis( name='synth' )
pnr      = PlaceAndRoute( name='pnr' )
pwr      = PowerAnalysis( name='pwr' )
summary  = Summary( name='summary' )

#-------------------------------------------------------------------------
# Instantiate the flow
#-------------------------------------------------------------------------

with Flow( 'ece5745' ) as flow:
  adk = getadk()
  rtl = block()
  saif = vcd2saif( vcd=rtl )
  netlist = synth( adk=adk, verilog=rtl, saif=saif )
  pnr_res = pnr( adk=adk, netlist=netlist )
  pwr_rpt = pwr( adk=adk, saif=saif, namemap=netlist, verilog=pnr_res )
  summary( post_pnr_reports=pnr_res, power_reports=pwr_rpt, saif=saif )

