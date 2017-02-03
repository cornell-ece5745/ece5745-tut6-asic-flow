##########################################################################################
# Version: D-2010.03-SP2 (July 6, 2010)
# Copyright (C) 2007-2010 Synopsys, Inc. All rights reserved.
##########################################################################################
source -echo icc_setup.tcl

###################################################
## chip_finish_icc: Several chipfinishing steps  ##
###################################################




open_mw_lib $MW_DESIGN_LIBRARY
redirect /dev/null "remove_mw_cel -version_kept 0 ${ICC_CHIP_FINISH_CEL}"
copy_mw_cel -from $ICC_ROUTE_OPT_CEL -to $ICC_CHIP_FINISH_CEL
open_mw_cel $ICC_CHIP_FINISH_CEL


source -echo common_optimization_settings_icc.tcl
source -echo common_placement_settings_icc.tcl
source -echo common_post_cts_timing_settings.tcl



########################################
#    LOAD THE ROUTE AND SI SETTINGS    #
########################################

source -echo common_route_si_settings_zrt_icc.tcl

##Turn of soft spacing for timing optimization during chip finishing
set_route_zrt_detail_options -eco_route_use_soft_spacing_for_timing_optimization false



if { [check_error -verbose] != 0} { echo "SCRIPT-Error, flagging ..." }

if {$ICC_REDUCE_CRITICAL_AREA } {

  ########################################
  #      CRITICAL AREA REDUCTION          #
  ########################################

  ## Timing driven wire spreading for shorts and widening for opens
  ## It is recommended to define a slack threshold to avoid that nets with too small slack are touched
  ## the unit of $TIMING_PRESERVE_SLACK_SETUP and $TIMING_PRESERVE_SLACK_HOLD is the library unit, so make sure that you provide the correct
  ## values in case your library has ps as unit. Default are 0.1 and 0, i.e. 0.1ns and 0ns, respectively.
  spread_zrt_wires -timing_preserve_setup_slack_threshold $TIMING_PRESERVE_SLACK_SETUP -timing_preserve_hold_slack_threshold $TIMING_PRESERVE_SLACK_HOLD
  widen_zrt_wires -timing_preserve_setup_slack_threshold $TIMING_PRESERVE_SLACK_SETUP -timing_preserve_hold_slack_threshold $TIMING_PRESERVE_SLACK_HOLD

  if { [check_error -verbose] != 0} { echo "SCRIPT-Error, flagging ..." }
}

if {$ICC_FIX_ANTENNA } {

  ########################################
  #        ANTENNA DIODE FIXING          #
  ########################################

  if { $ICC_USE_DIODES && [file exists [which $ANTENNA_RULES_FILE]] && $ICC_ROUTING_DIODES != ""} {
       set_route_zrt_detail_options -antenna true -diode_libcell_names $ICC_ROUTING_DIODES -insert_diodes_during_routing true
       route_zrt_detail -incremental true
   }

}


  ###################################
  #          SHIELDING              #
  ###################################

  ##Shield Clocks/Nets if Constraint Set Previously
  # create_zrt_shield
  # set_route_zrt_common_options -reshield_modified_nets reshield
  # set_extraction_options -virtual_shield_extraction false



if {$ADD_FILLER_CELL } {

  ########################################
  #          STD CELL FILLERS            #
  ########################################

##Filler Cells
## stdcell filler for MultiVth designs
## https://solvnet.synopsys.com/retrieve/025405.html:
##
## set_cell_vt_type -library ./libs/cmos10lphvt -vt_type vtType0
## set_cell_vt_type -library ./libs/cmos10lplvt -vt_type vtType1
## set_vt_filler_rule -threshold_voltage "vtType0 vtType1" \
##     -lib_cell "STH_FILL64 STH_FILL32 STH_FILL16 STH_FILL8 STH_FILL4 STH_FILL2 STH_FILL1"
##  # use HT fillers between ST & HT cells
##
## set_vt_filler_rule -threshold_voltage "vtType0 vtType0" \
##     -lib_cell "STH_FILL64 STH_FILL32 STH_FILL16 STH_FILL8 STH_FILL4 STH_FILL2 STH_FILL1"
##  # use HT fillers between HT & HT cells
##
## set_vt_filler_rule -threshold_voltage "vtType1 vtType1" \
##     -lib_cell "STN_FILL64 STN_FILL32 STN_FILL16 STN_FILL8 STN_FILL4 STN_FILL2 STN_FILL1"
##  # use ST fillers between ST & ST cells
##
##
## insert_stdcell_filler -respect_overlap -connect_to_power VDD -connect_to_ground VSS
##
## Constrained decoupling capacitor insertion UI :
#  insert_stdcell_filler -leakage_power <mW> -metal_filler_coverage_area <um^2>

   if {$FILLER_CELL_METAL != ""} {insert_stdcell_filler -cell_with_metal $FILLER_CELL_METAL -connect_to_power $MW_POWER_NET -connect_to_ground $MW_GROUND_NET}
   if {$FILLER_CELL != ""} {insert_stdcell_filler -cell_without_metal $FILLER_CELL -connect_to_power $MW_POWER_NET -connect_to_ground $MW_GROUND_NET}


if { [check_error -verbose] != 0} { echo "SCRIPT-Error, flagging ..." }

}


if {$ICC_FIX_ANTENNA || $ICC_REDUCE_CRITICAL_AREA || $ADD_FILLER_CELL } {

  ########################################
  #     INCREMENTAL TIMING OPTO          #
  ########################################

  route_opt -incremental -size_only

  if { [check_error -verbose] != 0} { echo "SCRIPT-Error, flagging ..." }

}
if {$ICC_DBL_VIA } {

  ## Optionally, if DV is really a key issue, we recommend to run a 3rd time
  ## but with timing preserve on, so that any critical paths are not touched by this step.
  ########################################
  #           REDUNDANT VIA              #
  ########################################

  if {$ICC_DBL_VIA_FLOW_EFFORT == "HIGH"} {
   insert_zrt_redundant_vias -effort medium \
                             -timing_preserve_setup_slack_threshold $TIMING_PRESERVE_SLACK_SETUP \
                             -timing_preserve_hold_slack_threshold $TIMING_PRESERVE_SLACK_HOLD

   if { [check_error -verbose] != 0} { echo "SCRIPT-Error, flagging ..." }
  }



}


if {$ADD_FILLER_CELL } {

  ########################################
  #          STD CELL FILLERS            #
  ########################################

##Filler Cells
    if {$FILLER_CELL != ""} {insert_stdcell_filler -cell_without_metal $FILLER_CELL -connect_to_power $MW_POWER_NET -connect_to_ground $MW_GROUND_NET}


if { [check_error -verbose] != 0} { echo "SCRIPT-Error, flagging ..." }

}


####Signal EM
## All details of the ICC Signal EM flow are found here :
## https://solvnet.synopsys.com/retrieve/023849.html
## Example : must load Signal EM constraints using Milkyway tool into design library using ALF or PLIB
## read_saif -input switching.saif
## set_switching_activity -toggle_rate 1.0 -static_probability 0.5 [get_nets -hier *]
## propagate_switching_activity
## update_timing
## report_signal_em -repair "repair.file.tcl" -verbose [get_nets -hier *] > signal_em.rpt
## source repair.file.tcl
## #remove_net_routing list_of_nets_in_repair_file ;#since zroute will not see width changes
## route_zrt_eco

########################################
#           CONNECT P/G                #
########################################


## Connect Power & Ground for non-MV and MV-mode

 if {[file exists [which $CUSTOM_CONNECT_PG_NETS_SCRIPT]]} {
   source -echo $CUSTOM_CONNECT_PG_NETS_SCRIPT
 } else {
    derive_pg_connection -power_net $MW_POWER_NET -power_pin $MW_POWER_PORT -ground_net $MW_GROUND_NET -ground_pin $MW_GROUND_PORT
    if {!$ICC_TIE_CELL_FLOW} {derive_pg_connection -power_net $MW_POWER_NET -ground_net $MW_GROUND_NET -tie}
   }
if { [check_error -verbose] != 0} { echo "SCRIPT-Error, flagging ..." }
##Final Route clean-up - if needed:
##Once we hit minor cleanup, best to turn off ZRoute timing options
##This avoids extraction/timing hits
set_route_zrt_global_options -timing_driven false -crosstalk_driven false
set_route_zrt_track_options -timing_driven false -crosstalk_driven false
set_route_zrt_detail_options -timing_driven false

route_zrt_eco               ;#catch any opens and try to re-route them, recheck DRC
if {$ICC_REPORTING_EFFORT != "OFF" } {
  redirect -tee -file $REPORTS_DIR_CHIP_FINISH/$ICC_CHIP_FINISH_CEL.qor {report_qor}
  redirect -file $REPORTS_DIR_CHIP_FINISH/$ICC_CHIP_FINISH_CEL.con {report_constraints}
}

if {$ICC_REPORTING_EFFORT != "OFF" } {
     redirect -tee -file $REPORTS_DIR_CHIP_FINISH/$ICC_CHIP_FINISH_CEL.clock_tree {report_clock_tree -summary}     ;# global skew report
     redirect -file $REPORTS_DIR_CHIP_FINISH/$ICC_CHIP_FINISH_CEL.clock_timing {report_clock_timing -type skew} ;# local skew report
}
if {$ICC_REPORTING_EFFORT != "OFF" } {
 redirect -file $REPORTS_DIR_CHIP_FINISH/$ICC_CHIP_FINISH_CEL.max.tim {report_timing -crosstalk_delta -capacitance -transition_time -input_pins -nets -delay max}
 redirect -file $REPORTS_DIR_CHIP_FINISH/$ICC_CHIP_FINISH_CEL.min.tim {report_timing -crosstalk_delta -capacitance -transition_time -input_pins -nets -delay min}
}
#    verify_zrt_route -antenna true
#    verify_zrt_route -antenna false
if {$ICC_REPORTING_EFFORT != "OFF" } {
 redirect -tee -file $REPORTS_DIR_CHIP_FINISH/$ICC_CHIP_FINISH_CEL.sum {report_design_physical -all -verbose}
}

save_mw_cel -as $ICC_CHIP_FINISH_CEL

# YUNSUP: add reports
redirect -file $REPORTS_DIR/$ICC_CHIP_FINISH_CEL.clock_tree.rpt {report_clock_tree -summary}
redirect -file $REPORTS_DIR/$ICC_CHIP_FINISH_CEL.clock_timing.rpt {report_clock_timing -type skew}
redirect -file $REPORTS_DIR/$ICC_CHIP_FINISH_CEL.qor.rpt {report_qor}
redirect -file $REPORTS_DIR/$ICC_CHIP_FINISH_CEL.timing.rpt {report_timing -input_pins -capacitance -transition_time -nets -significant_digits 4 -attributes -nosplit -nworst 10 -max_paths 500}
redirect -file $REPORTS_DIR/$ICC_CHIP_FINISH_CEL.area.rpt {report_area -nosplit -hierarchy}
redirect -file $REPORTS_DIR/$ICC_CHIP_FINISH_CEL.power.rpt {report_power -nosplit -hier}
redirect -file $REPORTS_DIR/$ICC_CHIP_FINISH_CEL.reference.rpt {report_reference -nosplit -hierarchy}
redirect -file $REPORTS_DIR/$ICC_CHIP_FINISH_CEL.sum.rpt {report_design_physical -all -verbose}

if {$ICC_REPORTING_EFFORT != "OFF" } {
 create_qor_snapshot -clock_tree -name $ICC_CHIP_FINISH_CEL
 redirect -file $REPORTS_DIR_CHIP_FINISH/$ICC_CHIP_FINISH_CEL.qor_snapshot.rpt {report_qor_snapshot -no_display}
}


exit
