//========================================================================
// RegIncrNstage
//========================================================================
// Registered incrementer that is parameterized by the number of stages.

`ifndef TUT4_VERILOG_REGINCR_REG_INCR_NSTAGE_V
`define TUT4_VERILOG_REGINCR_REG_INCR_NSTAGE_V

`include "tut4_verilog/regincr/RegIncr.v"

module tut4_verilog_regincr_RegIncrNstage
#(
  parameter p_nstages = 2
)(
  input  logic       clk,
  input  logic       reset,
  input  logic [7:0] in_,
  output logic [7:0] out
);

  // This defines an _array_ of signals. There are p_nstages+1 signals
  // and each signal is 8 bits wide. We will use this array of signals to
  // hold the output of each registered incrementer stage.

  logic [7:0] reg_incr_out [p_nstages+1];

  // Connect the input port of the module to the first signal in the
  // reg_incr_out signal array.

  assign reg_incr_out[0] = in_;

  // Instantiate the registered incrementers and make the connections
  // between them using a generate block.

  genvar i;
  generate
  for ( i = 0; i < p_nstages; i = i + 1 ) begin: gen

    tut4_verilog_regincr_RegIncr reg_incr
    (
      .clk   (clk),
      .reset (reset),
      .in_   (reg_incr_out[i]),
      .out   (reg_incr_out[i+1])
    );

  end
  endgenerate

  // Connect the last signal in the reg_incr_out signal array to the
  // output port of the module.

  assign out = reg_incr_out[p_nstages];

endmodule

`endif /* TUT4_VERILOG_REGINCR_REG_INCR_NSTAGE_V */

