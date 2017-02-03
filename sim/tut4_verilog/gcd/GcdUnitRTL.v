//========================================================================
// GCD Unit RTL Implementation
//========================================================================

`ifndef TUT4_VERILOG_GCD_GCD_UNIT_V
`define TUT4_VERILOG_GCD_GCD_UNIT_V

`include "vc/muxes.v"
`include "vc/regs.v"
`include "vc/arithmetic.v"
`include "vc/trace.v"

//========================================================================
// GCD Unit Datapath
//========================================================================

module tut4_verilog_gcd_GcdUnitDpath
(
  input  logic        clk,
  input  logic        reset,

  // Data signals

  input  logic [31:0] req_msg,
  output logic [15:0] resp_msg,

  // Control signals

  input  logic        a_reg_en,   // Enable for A register
  input  logic        b_reg_en,   // Enable for B register
  input  logic [1:0]  a_mux_sel,  // Sel for mux in front of A reg
  input  logic        b_mux_sel,  // sel for mux in front of B reg

  // Status signals

  output logic        is_b_zero,  // Output of zero comparator
  output logic        is_a_lt_b   // Output of less-than comparator
);

  localparam c_nbits = 16;

  // Split out the a and b operands

  logic [c_nbits-1:0] req_msg_a;
  assign req_msg_a = req_msg[31:16];

  logic [c_nbits-1:0] req_msg_b;
  assign req_msg_b = req_msg[15:0];

  // A Mux

  logic [c_nbits-1:0] b_reg_out;
  logic [c_nbits-1:0] sub_out;
  logic [c_nbits-1:0] a_mux_out;

  vc_Mux3#(c_nbits) a_mux
  (
    .sel   (a_mux_sel),
    .in0   (req_msg_a),
    .in1   (b_reg_out),
    .in2   (sub_out),
    .out   (a_mux_out)
  );

  // A register

  logic [c_nbits-1:0] a_reg_out;

  vc_EnReg#(c_nbits) a_reg
  (
    .clk   (clk),
    .reset (reset),
    .en    (a_reg_en),
    .d     (a_mux_out),
    .q     (a_reg_out)
  );

  // B Mux

  logic [c_nbits-1:0] b_mux_out;

  vc_Mux2#(c_nbits) b_mux
  (
    .sel   (b_mux_sel),
    .in0   (req_msg_b),
    .in1   (a_reg_out),
    .out   (b_mux_out)
  );

  // B register

  vc_EnReg#(c_nbits) b_reg
  (
    .clk   (clk),
    .reset (reset),
    .en    (b_reg_en),
    .d     (b_mux_out),
    .q     (b_reg_out)
  );

  // Less-than comparator

  vc_LtComparator#(c_nbits) a_lt_b
  (
    .in0   (a_reg_out),
    .in1   (b_reg_out),
    .out   (is_a_lt_b)
  );

  // Zero comparator

  vc_ZeroComparator#(c_nbits) b_zero
  (
    .in    (b_reg_out),
    .out   (is_b_zero)
  );

  // Subtractor

  vc_Subtractor#(c_nbits) sub
  (
    .in0   (a_reg_out),
    .in1   (b_reg_out),
    .out   (sub_out)
  );

  // Connect to output port

  assign resp_msg = sub_out;

endmodule

//========================================================================
// GCD Unit Control
//========================================================================

module tut4_verilog_gcd_GcdUnitCtrl
(
  input  logic        clk,
  input  logic        reset,

  // Dataflow signals

  input  logic        req_val,
  output logic        req_rdy,
  output logic        resp_val,
  input  logic        resp_rdy,

  // Control signals

  output logic        a_reg_en,   // Enable for A register
  output logic        b_reg_en,   // Enable for B register
  output logic [1:0]  a_mux_sel,  // Sel for mux in front of A reg
  output logic        b_mux_sel,  // sel for mux in front of B reg

  // Data signals

  input  logic        is_b_zero,  // Output of zero comparator
  input  logic        is_a_lt_b   // Output of less-than comparator
);

  //----------------------------------------------------------------------
  // State Definitions
  //----------------------------------------------------------------------

  localparam STATE_IDLE = 2'd0;
  localparam STATE_CALC = 2'd1;
  localparam STATE_DONE = 2'd2;

  //----------------------------------------------------------------------
  // State
  //----------------------------------------------------------------------

  logic [1:0] state_reg;
  logic [1:0] state_next;

  always_ff @( posedge clk ) begin
    if ( reset ) begin
      state_reg <= STATE_IDLE;
    end
    else begin
      state_reg <= state_next;
    end
  end

  //----------------------------------------------------------------------
  // State Transitions
  //----------------------------------------------------------------------

  logic req_go;
  logic resp_go;
  logic is_calc_done;

  assign req_go       = req_val  && req_rdy;
  assign resp_go      = resp_val && resp_rdy;
  assign is_calc_done = !is_a_lt_b && is_b_zero;

  always_comb begin

    state_next = state_reg;

    case ( state_reg )

      STATE_IDLE: if ( req_go    )    state_next = STATE_CALC;
      STATE_CALC: if ( is_calc_done ) state_next = STATE_DONE;
      STATE_DONE: if ( resp_go   )    state_next = STATE_IDLE;
      default:    state_next = 'x;

    endcase

  end

  //----------------------------------------------------------------------
  // State Outputs
  //----------------------------------------------------------------------

  localparam a_x   = 2'dx;
  localparam a_ld  = 2'd0;
  localparam a_b   = 2'd1;
  localparam a_sub = 2'd2;

  localparam b_x   = 1'dx;
  localparam b_ld  = 1'd0;
  localparam b_a   = 1'd1;

  function void cs
  (
    input logic       cs_req_rdy,
    input logic       cs_resp_val,
    input logic [1:0] cs_a_mux_sel,
    input logic       cs_a_reg_en,
    input logic       cs_b_mux_sel,
    input logic       cs_b_reg_en
  );
  begin
    req_rdy   = cs_req_rdy;
    resp_val  = cs_resp_val;
    a_reg_en  = cs_a_reg_en;
    b_reg_en  = cs_b_reg_en;
    a_mux_sel = cs_a_mux_sel;
    b_mux_sel = cs_b_mux_sel;
  end
  endfunction

  // Labels for Mealy transistions

  logic do_swap;
  logic do_sub;

  assign do_swap = is_a_lt_b;
  assign do_sub  = !is_b_zero;

  // Set outputs using a control signal "table"

  always_comb begin

    cs( 0, 0, a_x, 0, b_x, 0 );
    case ( state_reg )
      //                             req resp a mux  a  b mux b
      //                             rdy val  sel    en sel   en
      STATE_IDLE:                cs( 1,  0,   a_ld,  1, b_ld, 1 );
      STATE_CALC: if ( do_swap ) cs( 0,  0,   a_b,   1, b_a,  1 );
             else if ( do_sub  ) cs( 0,  0,   a_sub, 1, b_x,  0 );
      STATE_DONE:                cs( 0,  1,   a_x,   0, b_x,  0 );
      default                    cs('x, 'x,   a_x,  'x, b_x, 'x );

    endcase

  end

endmodule

//========================================================================
// GCD Unit
//========================================================================

module tut4_verilog_gcd_GcdUnitRTL
(
  input  logic             clk,
  input  logic             reset,

  input  logic             req_val,
  output logic             req_rdy,
  input  logic [31:0]      req_msg,

  output logic             resp_val,
  input  logic             resp_rdy,
  output logic [15:0]      resp_msg
);

  //----------------------------------------------------------------------
  // Connect Control Unit and Datapath
  //----------------------------------------------------------------------

  // Control signals

  logic        a_reg_en;
  logic        b_reg_en;
  logic [1:0]  a_mux_sel;
  logic        b_mux_sel;

  // Data signals

  logic        is_b_zero;
  logic        is_a_lt_b;

  // Control unit

  tut4_verilog_gcd_GcdUnitCtrl ctrl
  (
    .*
  );

  // Datapath

  tut4_verilog_gcd_GcdUnitDpath dpath
  (
    .*
  );

  //----------------------------------------------------------------------
  // Line Tracing
  //----------------------------------------------------------------------

  `ifndef SYNTHESIS

  logic [`VC_TRACE_NBITS-1:0] str;
  `VC_TRACE_BEGIN
  begin

    $sformat( str, "%x:%x", req_msg[31:16], req_msg[15:0] );
    vc_trace.append_val_rdy_str( trace_str, req_val, req_rdy, str );

    vc_trace.append_str( trace_str, "(" );

    $sformat( str, "%x", dpath.a_reg_out );
    vc_trace.append_str( trace_str, str );
    vc_trace.append_str( trace_str, " " );

    $sformat( str, "%x", dpath.b_reg_out );
    vc_trace.append_str( trace_str, str );
    vc_trace.append_str( trace_str, " " );

    case ( ctrl.state_reg )

      ctrl.STATE_IDLE:
        vc_trace.append_str( trace_str, "I " );

      ctrl.STATE_CALC:
      begin
        if ( ctrl.do_swap )
          vc_trace.append_str( trace_str, "Cs" );
        else if ( ctrl.do_sub )
          vc_trace.append_str( trace_str, "C-" );
        else
          vc_trace.append_str( trace_str, "C " );
      end

      ctrl.STATE_DONE:
        vc_trace.append_str( trace_str, "D " );

      default:
        vc_trace.append_str( trace_str, "? " );

    endcase

    vc_trace.append_str( trace_str, ")" );

    $sformat( str, "%x", resp_msg );
    vc_trace.append_val_rdy_str( trace_str, resp_val, resp_rdy, str );

  end
  `VC_TRACE_END

  `endif /* SYNTHESIS */

endmodule

`endif /* TUT4_VERILOG_GCD_GCD_UNIT_V */

