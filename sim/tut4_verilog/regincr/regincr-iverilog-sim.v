//========================================================================
// RegIncr Ad-Hoc Testing
//========================================================================

`include "../tut4_verilog/regincr/RegIncr.v"

module top;

  // Clocking

  logic clk = 1;
  always #5 clk = ~clk;

  // Instaniate the design under test

  logic       reset = 1;
  logic [7:0] in;
  logic [7:0] out;

  // ''' TUTORIAL TASK '''''''''''''''''''''''''''''''''''''''''''''''''''
  // This simulator script is incomplete. As part of the tutorial you
  // will need to instantiate and connect a RegIncr model here.
  // '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

  // Verify functionality

  initial begin

    // Dump waveforms

    $dumpfile("regincr-iverilog-sim.vcd");
    $dumpvars;

    // Reset

    #11;
    reset = 1'b0;

    // Test cases

    in = 8'h00;
    #10;
    if ( out != 8'h01 ) begin
      $display( "ERROR: out, expected = %x, actual = %x", 8'h01, out );
      $finish;
    end

    in = 8'h13;
    #10;
    if ( out != 8'h14 ) begin
      $display( "ERROR: out, expected = %x, actual = %x", 8'h14, out );
      $finish;
    end

    in = 8'h27;
    #10;
    if ( out != 8'h28 ) begin
      $display( "ERROR: out, expected = %x, actual = %x", 8'h28, out );
      $finish;
    end

    $display( "*** PASSED ***" );
    $finish;
  end

endmodule

