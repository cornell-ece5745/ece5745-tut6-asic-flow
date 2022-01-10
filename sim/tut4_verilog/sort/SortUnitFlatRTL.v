//========================================================================
// Simple Four-Element Sorting Unit
//========================================================================
// This module sorts four N-bit elements into ascending order using a
// merge-sort-like hardware algorithm unrolled in space. We break the
// four elements into two pairs and sort each pair independently. Then we
// compare the smaller elements from each pair and the larger elements
// from each pair before arranging the middle two elements.
//
// This implementation uses a flat RTL coding style and is pipelined into
// three stages with exactly one comparison along the critical path in
// each stage.

`ifndef TUT4_VERILOG_SORT_SORT_UNIT_FLAT_V
`define TUT4_VERILOG_SORT_SORT_UNIT_FLAT_V

`include "vc/trace.v"

module tut4_verilog_sort_SortUnitFlatRTL
#(
  parameter p_nbits = 1
)(
  input  logic               clk,
  input  logic               reset,

  input  logic               in_val,
  input  logic [p_nbits-1:0] in0,
  input  logic [p_nbits-1:0] in1,
  input  logic [p_nbits-1:0] in2,
  input  logic [p_nbits-1:0] in3,

  output logic               out_val,
  output logic [p_nbits-1:0] out0,
  output logic [p_nbits-1:0] out1,
  output logic [p_nbits-1:0] out2,
  output logic [p_nbits-1:0] out3
);

  //----------------------------------------------------------------------
  // Stage S0->S1 pipeline registers
  //----------------------------------------------------------------------

  logic               val_S1;
  logic [p_nbits-1:0] elm0_S1;
  logic [p_nbits-1:0] elm1_S1;
  logic [p_nbits-1:0] elm2_S1;
  logic [p_nbits-1:0] elm3_S1;

  always_ff @( posedge clk ) begin
    val_S1  <= (reset) ? 0 : in_val;
    elm0_S1 <= in0;
    elm1_S1 <= in1;
    elm2_S1 <= in2;
    elm3_S1 <= in3;
  end

  //----------------------------------------------------------------------
  // Stage S1 combinational logic
  //----------------------------------------------------------------------
  // Note that we explicitly catch the case where the elements contain
  // X's and propagate X's appropriately. We would not need to do this if
  // we used a continuous assignment statement with a ternary conditional
  // operator.

  logic [p_nbits-1:0] elm0_next_S1;
  logic [p_nbits-1:0] elm1_next_S1;
  logic [p_nbits-1:0] elm2_next_S1;
  logic [p_nbits-1:0] elm3_next_S1;

  always_comb begin

    // Sort elms 0 and 1

    if ( elm0_S1 <= elm1_S1 ) begin
      elm0_next_S1 = elm0_S1;
      elm1_next_S1 = elm1_S1;
    end
    else if ( elm0_S1 > elm1_S1 ) begin
      elm0_next_S1 = elm1_S1;
      elm1_next_S1 = elm0_S1;
    end
    else begin
      elm0_next_S1 = 'x;
      elm1_next_S1 = 'x;
    end

    // Sort elms 2 and 3

    if ( elm2_S1 <= elm3_S1 ) begin
      elm2_next_S1 = elm2_S1;
      elm3_next_S1 = elm3_S1;
    end
    else if ( elm2_S1 > elm3_S1 ) begin
      elm2_next_S1 = elm3_S1;
      elm3_next_S1 = elm2_S1;
    end
    else begin
      elm2_next_S1 = 'x;
      elm3_next_S1 = 'x;
    end

  end

  //----------------------------------------------------------------------
  // Stage S1->S2 pipeline registers
  //----------------------------------------------------------------------

  logic               val_S2;
  logic [p_nbits-1:0] elm0_S2;
  logic [p_nbits-1:0] elm1_S2;
  logic [p_nbits-1:0] elm2_S2;
  logic [p_nbits-1:0] elm3_S2;

  always_ff @( posedge clk ) begin
    val_S2  <= (reset) ? 0 : val_S1;
    elm0_S2 <= elm0_next_S1;
    elm1_S2 <= elm1_next_S1;
    elm2_S2 <= elm2_next_S1;
    elm3_S2 <= elm3_next_S1;
  end

  //----------------------------------------------------------------------
  // Stage S2 combinational logic
  //----------------------------------------------------------------------

  logic [p_nbits-1:0] elm0_next_S2;
  logic [p_nbits-1:0] elm1_next_S2;
  logic [p_nbits-1:0] elm2_next_S2;
  logic [p_nbits-1:0] elm3_next_S2;

  always_comb begin

    // Sort elms 0 and 2

    if ( elm0_S2 <= elm2_S2 ) begin
      elm0_next_S2 = elm0_S2;
      elm2_next_S2 = elm2_S2;
    end
    else if ( elm0_S2 > elm2_S2 ) begin
      elm0_next_S2 = elm2_S2;
      elm2_next_S2 = elm0_S2;
    end
    else begin
      elm0_next_S2 = 'x;
      elm2_next_S2 = 'x;
    end

    // Sort elms 1 and 3

    if ( elm1_S2 <= elm3_S2 ) begin
      elm1_next_S2 = elm1_S2;
      elm3_next_S2 = elm3_S2;
    end
    else if ( elm1_S2 > elm3_S2 ) begin
      elm1_next_S2 = elm3_S2;
      elm3_next_S2 = elm1_S2;
    end
    else begin
      elm1_next_S2 = 'x;
      elm3_next_S2 = 'x;
    end

  end

  //----------------------------------------------------------------------
  // Stage S2->S3 pipeline registers
  //----------------------------------------------------------------------

  logic               val_S3;
  logic [p_nbits-1:0] elm0_S3;
  logic [p_nbits-1:0] elm1_S3;
  logic [p_nbits-1:0] elm2_S3;
  logic [p_nbits-1:0] elm3_S3;

  always_ff @( posedge clk ) begin
    val_S3  <= (reset) ? 0 : val_S2;
    elm0_S3 <= elm0_next_S2;
    elm1_S3 <= elm1_next_S2;
    elm2_S3 <= elm2_next_S2;
    elm3_S3 <= elm3_next_S2;
  end

  //----------------------------------------------------------------------
  // Stage S3 combinational logic
  //----------------------------------------------------------------------

  logic [p_nbits-1:0] elm0_next_S3;
  logic [p_nbits-1:0] elm1_next_S3;
  logic [p_nbits-1:0] elm2_next_S3;
  logic [p_nbits-1:0] elm3_next_S3;

  always_comb begin

    // Pass through elms 0 and 3

    elm0_next_S3 = elm0_S3;
    elm3_next_S3 = elm3_S3;

    // Sort elms 1 and 2

    if ( elm1_S3 <= elm2_S3 ) begin
      elm1_next_S3 = elm1_S3;
      elm2_next_S3 = elm2_S3;
    end
    else if ( elm1_S3 > elm2_S3 ) begin
      elm1_next_S3 = elm2_S3;
      elm2_next_S3 = elm1_S3;
    end
    else begin
      elm1_next_S3 = 'x;
      elm2_next_S3 = 'x;
    end

  end

  // Assign output ports

  assign out_val = val_S3;
  assign out0    = elm0_next_S3 & {p_nbits{out_val}};
  assign out1    = elm1_next_S3 & {p_nbits{out_val}};
  assign out2    = elm2_next_S3 & {p_nbits{out_val}};
  assign out3    = elm3_next_S3 & {p_nbits{out_val}};

  //----------------------------------------------------------------------
  // Assertions
  //----------------------------------------------------------------------

  `ifndef SYNTHESIS
  always_ff @( posedge clk ) begin
    if ( !reset ) begin
      assert ( ^in_val  !== 1'bx );
      assert ( ^val_S1  !== 1'bx );
      assert ( ^val_S2  !== 1'bx );
      assert ( ^val_S3  !== 1'bx );
      assert ( ^out_val !== 1'bx );
    end
  end
  `endif /* SYNTHESIS */

  //----------------------------------------------------------------------
  // Line Tracing
  //----------------------------------------------------------------------

  `ifndef SYNTHESIS

  logic [`VC_TRACE_NBITS-1:0] str;
  `VC_TRACE_BEGIN
  begin

    // Inputs

    $sformat( str, "{%x,%x,%x,%x}", in0, in1, in2, in3 );
    vc_trace.append_val_str( trace_str, in_val, str  );
    vc_trace.append_str( trace_str, "|" );

    // Pipeline stage S1

    $sformat( str, "{%x,%x,%x,%x}", elm0_S1, elm1_S1, elm2_S1, elm3_S1 );
    vc_trace.append_val_str( trace_str, val_S1, str  );
    vc_trace.append_str( trace_str, "|" );

    // Pipeline stage S2

    $sformat( str, "{%x,%x,%x,%x}", elm0_S2, elm1_S2, elm2_S2, elm3_S2 );
    vc_trace.append_val_str( trace_str, val_S2, str  );
    vc_trace.append_str( trace_str, "|" );

    // Pipeline stage S3

    $sformat( str, "{%x,%x,%x,%x}", elm0_S3, elm1_S3, elm2_S3, elm3_S3 );
    vc_trace.append_val_str( trace_str, val_S3, str  );
    vc_trace.append_str( trace_str, "|" );

    // Outputs

    $sformat( str, "{%x,%x,%x,%x}", out0, out1, out2, out3 );
    vc_trace.append_val_str( trace_str, out_val, str  );

  end
  `VC_TRACE_END

  `endif /* SYNTHESIS */

endmodule

`endif /* TUT4_VERILOG_SORT_SORT_UNIT_FLAT_V */
