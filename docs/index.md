
ECE 5745 Tutorial 6: Automated ASIC Flow
==========================================================================

 - Author: Christopher Batten, Yanghui Ou
 - Date: March 1, 2020

**Table of Contents**

 - Introduction
 - PyMTL-Based Testing, Simulation, Translation
 - Using Synopsys Design Compiler for Synthesis
 - Using Synopsys IC Compiler for Place-and-Route
 - Using Synopsys PrimeTime for Power Analysis
 - Using Verilog RTL Models
 - Using the Automated ASIC Flow for Design-Space Exploration
 - Pushing GCD Unit Through the Automated ASIC Flow

Introduction
--------------------------------------------------------------------------

The previous tutorial introduced students to the key tools used for
synthesis, place-and-route, and power analysis, but the previous tutorial
required students to enter commands manually for each tool. This is
obviously very tedious and error prone. An agile hardware design flow
demands automation to simplify rapidly exploring the area, energy, timing
design space of one or more designs. Luckily, Synopsys tools can be
easily scripted using TCL, and even better, the ECE 5745 staff have
already created these TCL scripts along with a set of Makefiles to run
these TCL scripts. The ECE 5745 TCL scripts were based on the Synopsys
reference methodology which is copyrighted by Synopsys. This means you
_cannot_ take this repo and/or the scripts and make them public. Please
keep this in mind.

The tutorial will describe how these scripts can make it relatively easy
to take designs from RTL to layout. We often call such a set of scripts
an "ASIC flow". However, it is critical for students to avoid thinking of
the ASIC flow as a black box. As in all engineering, garbage-in means
garbage-out. If you are not careful it is all to easy to use the ASIC
flow to analyze a completely invalid design. This tutorial assumes you
have already completed the tutorials on Linux, Git, PyMTL, Verilog, and
the Synopsys ASIC tools.

The following diagram illustrates the four primary tools we will be using
in ECE 5745. Notice that this toolflow diagram is higher level than the
one we used in the previous tutorial. This is because the ASIC flow
actually uses several additional other files, but at the same time, we
are less concerned about the details of every single step since we are
using automating the entire process. We can hopefully focus more on the
big picture of how the tools fit together at a high-level.

![](assets/fig/asic-flow.png)

 1. We use the PyMTL framework to test, verify, and evaluate the
    execution time (in cycles) of our design. This part of the flow is
    exactly the same as ECE 4750. Note that we can write our RTL models
    in either PyMTL or Verilog. Once we are sure our design is working
    correctly, we can then start to push the design through the flow. The
    ASIC flow requires Verilog RTL as an input, so we can use PyMTL's
    automatic translation tool to translate PyMTL RTL models into Verilog
    RTL.

 2. We use Synopsys Design Compiler (DC) to synthesize our design, which
    means to transform the Verilog RTL model into a Verilog gate-level
    netlist where all of the gates are selected from a standard cell
    library. We need to provide Synopsys DC with higher-level
    characterization information about our standard cell library.

 3. We use Cadence Innovus to place-and-route our design,
    which means to place all of the gates in the gate-level netlist into
    rows on the chip and then to generate the metal wires that connect
    all of the gates together. Cadence Innovus will also handle power and
    clock routing. We need to provide Cadence Innovus with lower-level
    characterization information about our standard cell library.
    Cadence Innovus also generates reports that can be used to more
    accurately characterize area and timing.

 4. We use Synopsys PrimeTime (PT) to perform power-analysis of our
    design. This requires switching activity information for every net in
    the design (which comes from the PyMTL simulator) and parasitic
    capacitance information for every net in the design (which comes from
    Cadence Innovus). Synopsys PT puts the switching activity, capacitance,
    clock frequency, and voltage together to estimate the power
    consumption of every net and thus every module in the design.

Extensive documentation is provided by Synopsys for Design Compiler, Cadence
Innovus, and Synopsys PrimeTime. We have organized this documentation and made it
available to you on the [public course
webpage](http://www.csl.cornell.edu/courses/ece5745/asicdocs). The
username/password was distributed during lecture.

The first step is to source the setup script, clone this repository from
GitHub, and define an environment variable to keep track of the top
directory for the project.

```
 % source setup-ece5745.sh
 % mkdir $HOME/ece5745
 % cd $HOME/ece5745
 % git clone git@github.com:cornell-ece5745/ece5745-tut6-asic-flow
 % cd ece5745-tut6-asic-flow
 % TOPDIR=$PWD
```

PyMTL-Based Testing, Simulation, Translation
--------------------------------------------------------------------------

As in the previous tutorial, our goal is to characterize the area,
energy, and timing for the sort unit from the PyMTL tutorial using the
ASIC tools. As a reminder, the sort unit takes as input four integers and
a valid bit and outputs those same four integers in increasing order with
the valid bit. The sort unit is implemented using a three-stage
pipelined, bitonic sorting network and the datapath is shown below.

![](assets/fig/sort-unit-dpath.png)

Let's start by running the tests for the sort unit and note that the
tests for the `SortUnitStructRTL` will fail. You can just copy over your
implementation of the `MinMaxUnit` from when you completed the PyMTL
tutorial. If you have not completed the PyMTL tutorial then go back and
do that now.

```
 % mkdir $TOPDIR/sim/build
 % cd $TOPDIR/sim/build
 % pytest ../tut3_pymtl/sort
 % pytest ../tut3_pymtl/sort --test-verilog
```

As we learned in the previous tutorial, the `--test-verilog` command line
option tells the PyMTL framework to first translate the sort unit into
Verilog, and then important it back into PyMTL to verify that the
translated Verilog is itself correct.

Let's experiment with an example which is valid PyMTL code, but does is
not translatable to illustrate the importance of testing with
`--test-verilog`. Instead of using an `if` statement to implement the
`MinMaxUnit`, maybe we want to be clever and use the built-in `min` and
`max` Python functions like this:

```python
from pymtl3 import *

class MinMaxUnit( Component ):

  # Constructor

  def construct( s, nbits ):

    s.in0     = InPort ( nbits )
    s.in1     = InPort ( nbits )
    s.out_min = OutPort( nbits )
    s.out_max = OutPort( nbits )

    @update
    def block():
      s.out_max @= max( s.in0, s.in1 )
      s.out_min @= min( s.in0, s.in1 )
```

Rerun the tests on the pure-PyMTL implementation:

```
 % cd $TOPDIR/sim/build
 % pytest ../tut3_pymtl/sort/test/MinMaxUnit_test.py
```

All of the tests should pass, but now try running the tests with
`--test-verilog`.

```
 % cd $TOPDIR/sim/build
 % pytest ../tut3_pymtl/sort/test/MinMaxUnit_test.py --test-verilog
 % pytest ../tut3_pymtl/sort/test/MinMaxUnit_test.py -x --tb=short --test-verilog
...
E   pymtl3.passes.rtlir.errors.PyMTLSyntaxError:
E   In file /home/yo96/ece5745/ece5745-labs/sim/tut3_pymtl/sort/MinMaxUnit.py, Line 28, Col 18:
E     s.out_max @= max( s.in0, s.in1 )
E                 ^
E   - <_ast.Name object at 0x7f9d58048b50> function is not found!
```

The error message indicates that there is a translation error. In other
words, using the `min`/`max` functions is perfectly valid PyMTL code, but
the translation tool does not know how to translate these constructs into
Verilog. If you stick to the PyMTL usage rules posted on the course
website, your code will _probably_ be translatable. However, it is not
that difficult to write reasonable PyMTL code that is not translatable,
_and_ there is no guarantee the translation tool will catch translation
errors and produce such a nice error message as shown above. Translation
errors can result in run-time errors when you use `--test-verilog` or
they can even simulate correctly but produce errors when you try and
synthesize the design. So remember to always use `--test-verilog` before
using the ASIC flow, and to look for errors from the translation tool,
Verilator, and/or Synopsys DC.

After running the tests we use the sort unit simulator to do the final
translation into Verilog and to dump the `.vcd` (Value Change Dump) file
that we want to use for power analysis.

```
 % cd $TOPDIR/sim/build
 % ../tut3_pymtl/sort/sort-sim --impl rtl-struct --stats --translate --dump-vcd
 num_cycles          = 105
 num_cycles_per_sort = 1.05
```

We now have both the translated Verilog for the sort unit, and the `.vcd`
file for a specific simulation, so we are ready to use the ASIC flow to
quantitatively evaluate the area, energy, and timing.

Using Synopsys Design Compiler for Synthesis
--------------------------------------------------------------------------

All scripts for the ASIC flow are contained within the `asic`
subdirectory. We will use PyHFlow to drive the ASIC flow, and a
`flow_tut6_sort.py` that describes the flow. Go into the `asic` subdirectory
and take a look at the `flow_tut6_sort.py`.

```
 % cd $TOPDIR/asic
 % less flow_tut6_sort.py
```

The `Block` step sets the path to the source file and some required
metadata of the flow, such as the top module name and the clock period.

```
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
```

The `files` variable is a list of source files that we want to push
through the flow, and in this case it contains the source verilog file
and the VCD that you generated earlier for power analysis.
`SortUnitStructRTL__nbits_8` is the name of the design. The `clk_period`
parameter is where you set the target clock period constraint for this
design.


Now all we need to do is to use pyhflow to configure the flow and run the
synthesis step like this:

```
 % cd $TOPDIR/asic
 % mkdir build
 % cd build
 % pyhflow configure ../flow_tut6_sort.py
 % pyhflow run synth
```

You will see pyhflow run some commands, start Synopsys DC, run some TCL
scripts, and then finish up. Essentially, the automated system is doing
the same thing as what we did in the previous tutorial.

The first thing to do after you finish synthesis for a new design is to
_look at the log file_! We cannot stress how importance this is. Synopsys
DC will often exit with an error or worse simply produce some warnings
which are actually catastrophic. If you just blindly use `make` and then
move on to Cadence Innovus there is a good chance you will be pushing a
completely broken design through the flow. There are many, many things
that can go wrong. You may have used the incorrect file/module names in
the `flow.py`, there might be code in your Verilog RTL that is not
synthesizable, or you might have a simulation/synthesis mismatch such
that the design you are pushing through the flow is not really what you
were simulating. This is not easy and there is no simple way to figure
out these issues, but you must start by looking for errors and warnings
in the log file like this:

```
 % cd $TOPDIR/asic/build
 % grep Error synth/dc.log
 % grep Warning synth/dc.log
```

There should be no errors, but there will usually be warnings. The hard
part is knowing which warnings you can ignore and which ones indicate
something more problematic. If you are using PyMTL, you will see many
warnings like this:

```
Warning: In design 'Reg__Type_Bits8', port 'reset[0]' is not connected to any nets. (LINT-28)
Warning: In design 'MinMaxUnit__nbits_8', port 'clk[0]' is not connected to any nets. (LINT-28)
Warning: In design 'MinMaxUnit__nbits_8', port 'reset[0]' is not connected to any nets. (LINT-28)
```

This is because PyMTL always adds a `clk` and `reset` port to every
module regardless of whether or not that module actually uses these
ports. You can safely ignore these warnings.

Regardless of which RTL language you are using, you might see warnings
like this:

```
Warning: DesignWare synthetic library dw_foundation.sldb is added to the synthetic_library in the current command. (UISN-40)
Warning: Verilog 'assign' or 'tran' statements are written out. (VO-4)
```

I am not quite clear why these are a problem, so you can safely ignore
these warnings. If you see errors or warnings related to unresolved
module instances or unconnected nets, then you need to dig in and fix
them. Again, there are no easy rules here. You must build your intuition
into which warnings are safe to ignore.

When the synthesis is completed you can take a look at the resulting
Verilog gate-level netlist here:

```
 % cd $TOPDIR/asic/build/synth
 % less outputs/post-synth.v
```

The automated system is also setup to output a bunch of reports. However,
as discussed in the previous tutorial, we usually don't use these reports
since the post-synthesis area, energy, and timing results can be
significantly different than the more accurate post-place-and-route
results.

However, there is a "resources" report that can be somewhat useful. You
can view the resources report like this:

```
 % cd $TOPDIR/asic/build/synth
 % less post_synth.resources.rpt

****************************************
Design : MinMaxUnit__nbits_8_3
****************************************

Resource Report for this hierarchy in file
        ./inputs/verilog/SortUnitStructRTL__nbits_8__pickled.v
=============================================================================
| Cell           | Module         | Parameters | Contained Operations       |
=============================================================================
| gte_x_1        | DW_cmp         | width=8    | gte_56 (SortUnitStructRTL__nbits_8__pickled.v:56) |
=============================================================================


Implementation Report
===============================================================================
|                    |                  | Current            | Set            |
| Cell               | Module           | Implementation     | Implementation |
===============================================================================
| gte_x_1            | DW_cmp           | apparch (area)     |                |
===============================================================================
```

When using the more sophisticated `compile_ultra` command, Synopsys DC
can recognize common arithmetic operators and instead of treating those
operators as generic boolean logic, Synopsys DC will swap in what are
called "DesignWare" components. These DesignWare components are
pre-optimized at the gate-level for a generic gate-level library, which
then is eventually mapped to the specific standard-cell library used for
synthesis. There are DesignWare components for adders, shifters,
multipliers, floating-point units, etc. You can read more about the
DesignWare comments in the Synopsys documentation on the [public course
webpage](http://www.csl.cornell.edu/courses/ece5745/asicdocs).

The resources report tells you what DesignWare components Synopsys DC has
automatically inferred. As an aside, if you want to use more complicated
components (e.g., a floating point unit) then Synopsys DC cannot infer
these components automatically; you need to explicitly instantiate these
components in your Verilog. From the report we can see that Synopsys DC
has inferred a `DW_cmp` component. You can learn more about this
component from the
[datasheet](http://www.csl.cornell.edu/courses/ece5745/asicdocs/dwbb_datasheets/dw01_cmp6.pdf).

The data sheet mentions that it has several possible arithmetic
implementations it can choose from to meet the specific area, energy,
timing constraints. It has a ripple-carry implementation, a
delay-optimized parallel-prefix implementation, and an area-optimized
implementation. DesignWare components can significantly improve the area,
energy, and timing of arithmetic circuits.

Using Cadence Innovus for Place-and-Route
--------------------------------------------------------------------------

We use Cadence Innovus for placing and routing standard cells, but also
for power routing and clock tree synthesis. The Verilog gate-level
netlist generated by Cadence Innovus has no physical information: it is
just a netlist, so the Cadence Innovus will first try and do a rough
placement of all of the gates into rows on the chip. Cadence Innovus will
then do some preliminary routing, and iterate between more and more
detailed placement and routing until it reaches the target cycle time (or
gives up). Cadence Innovus will also route all of the power and ground
rails in a grid and connect this grid to the power and ground pins of
each standard cell, and Cadence Innovus will automatically generate a
clock tree to distribute the clock to all sequential state elements with
hopefully low skew. The automated flow for place-and-route is much more
sophisticated compared to what we did in the previous tutorial.

We can use `pyhflow` to run Cadence Innovus like this:

```
 % cd $TOPDIR/asic/build
 % pyhflow run pnr
```

Place-and-route can take significantly longer than synthesis, so be
prepared to wait a while with larger designs. If you look at the output
scrolling by you will see some of the optimization passes as Cadence
Innovus attempts to iteratively improve the design. As with Synopsys DC,
you can search the logs to look for errors and/or warnings.

```
 % cd $TOPDIR/asic/build
 % grep ERROR pnr/*.log
 % grep WARNING pnr/*.log
```

However, usually we catch errors in Synopsys DC and after that we are all
set. So if you see errors in Cadence Innovus, you might want to go back
and see if there were any errors in Synopsys DC.

The automated system is also setup to output a bunch of reports in the
`pnr` directory. You might want to start with the timing
summary report. If you take a look that report you will see something
like this:

```
 % cd $TOPDIR/asic/build/pnr
 % less signoff.summary.gz
 ...

+--------------------+---------+---------+---------+---------+---------+---------+
|     Setup mode     |   all   | default | In2Out  | In2Reg  | Reg2Out | Reg2Reg |
+--------------------+---------+---------+---------+---------+---------+---------+
|           WNS (ns):|  0.155  |  0.000  |   N/A   |  0.938  |  0.155  |  0.244  |
|           TNS (ns):|  0.000  |  0.000  |   N/A   |  0.000  |  0.000  |  0.000  |
|    Violating Paths:|    0    |    0    |   N/A   |    0    |    0    |    0    |
|          All Paths:|   132   |    0    |   N/A   |   35    |   33    |   66    |
+--------------------+---------+---------+---------+---------+---------+---------+
|analysis_default    |  0.155  |  0.000  |   N/A   |  0.938  |  0.155  |  0.244  |
|                    |  0.000  |  0.000  |   N/A   |  0.000  |  0.000  |  0.000  |
|                    |    0    |    0    |   N/A   |    0    |    0    |    0    |
|                    |   132   |    0    |   N/A   |   35    |   33    |   66    |
+--------------------+---------+---------+---------+---------+---------+---------+
 ...
```

Paths are organized into four groups: In2Reg, Reg2Out, In2Out, and
Reg2Reg path groups. In2Reg paths start at an input port and end at a
register; Reg2Out paths start at a register and end at an output port;
In2Out paths start at an input port and end at an output port; and
Reg2Reg paths start at a register and end at register. The following
diagram is from Chapter 1 of the [Synopsys Timing Constraints and
Optimization User
Guide](http://www.csl.cornell.edu/courses/ece5745/syndocs/tcoug.pdf).

![](assets/fig/synopsys-path-groups.png)

We have setup the flow so that the tools have to fit all four of these
paths in a single cycle. The timing report shows the worst negative slack
(WNS) and total negative slack (TNS) within each path group. The overall
critical path for your design will be the worse critical path across all
four groups. WNS is calculated as the the target clock minus the longest
path. This is very important! If we have negative slack then the design
must run slower than this clock constraint, and if we have positive slack
then the design can run faster than this clock constraint. Again, the
actual cycle time is the calculated by subtracting the WNS from the
target clock period (and we must look across all four path groups to find
the overall critical path). So in this example the Reg2Out path group has
the worst cycle time of 1 - 0.155 = 0.845ns.

To figure out the actual critical path through the design you will need
to look in the detailed timing report for each path group. These timing
reports are organized such that the worst case path is shown first. This
means you cannot just look at one timing report for a path group! The
critical path might be in a different path group. So first, use the
timing summary report to figure out which path group contains the
critical path, and then look in the corresponding timing report to see
the critical path like this:

```
 % cd $TOPDIR/asic/build/pnr
 % less signoff_Reg2Out.tarpt.gz
 ...
Path 1: MET Late External Delay Assertion
Endpoint:   out[13]                  (^) checked with  leading edge of 'ideal_
clock'
Beginpoint: elm_S2S3__2/out_reg[1]/Q (^) triggered by  leading edge of 'ideal_
clock'
Path Groups: {Reg2Out}
Analysis View: analysis_default
Other End Arrival Time          0.000
- External Delay                0.000
+ Phase Shift                   1.000
+ CPPR Adjustment               0.000
= Required Time                 1.000
- Arrival Time                  0.845
= Slack Time                    0.155
     Clock Rise Edge                      0.000
     + Source Insertion Delay            -0.004
     = Beginpoint Arrival Time           -0.004
     +---------------------------------------------------------------------------------------------------------------------+
     |            Pin            | Edge |          Net           |            Cell            | Delay | Arrival | Required |
     |                           |      |                        |                            |       |  Time   |   Time   |
     |---------------------------+------+------------------------+----------------------------+-------+---------+----------|
     | clk[0]                    |  ^   | clk[0]                 |                            |       |  -0.004 |    0.152 |
     | elm_S2S3__2/out_reg[1]/CK |  ^   | clk[0]                 | DFF_X1                     | 0.003 |  -0.001 |    0.154 |
     | elm_S2S3__2/out_reg[1]/Q  |  ^   | elm_S2S3__out[2][1]    | DFF_X1                     | 0.087 |   0.086 |    0.242 |
     | minmax_S3/U2/A            |  ^   | elm_S2S3__out[2][1]    | INV_X1                     | 0.000 |   0.086 |    0.242 |
     | minmax_S3/U2/ZN           |  v   | minmax_S3/n10          | INV_X1                     | 0.015 |   0.101 |    0.256 |
     | minmax_S3/U6/C2           |  v   | minmax_S3/n10          | AOI222_X1                  | 0.000 |   0.101 |    0.256 |
     | minmax_S3/U6/ZN           |  ^   | minmax_S3/n1           | AOI222_X1                  | 0.107 |   0.208 |    0.363 |
     | minmax_S3/U8/C1           |  ^   | minmax_S3/n1           | AOI222_X1                  | 0.000 |   0.208 |    0.363 |
     | minmax_S3/U8/ZN           |  v   | minmax_S3/n2           | AOI222_X1                  | 0.046 |   0.254 |    0.410 |
     | minmax_S3/U9/C2           |  v   | minmax_S3/n2           | AOI222_X1                  | 0.000 |   0.255 |    0.410 |
     | minmax_S3/U9/ZN           |  ^   | minmax_S3/n3           | AOI222_X1                  | 0.119 |   0.373 |    0.528 |
     | minmax_S3/U11/C1          |  ^   | minmax_S3/n3           | AOI222_X1                  | 0.000 |   0.373 |    0.529 |
     | minmax_S3/U11/ZN          |  v   | minmax_S3/n4           | AOI222_X1                  | 0.047 |   0.421 |    0.576 |
     | minmax_S3/U12/C2          |  v   | minmax_S3/n4           | AOI222_X1                  | 0.000 |   0.421 |    0.576 |
     | minmax_S3/U12/ZN          |  ^   | minmax_S3/n5           | AOI222_X1                  | 0.117 |   0.538 |    0.693 |
     | minmax_S3/U14/C1          |  ^   | minmax_S3/n5           | AOI222_X1                  | 0.000 |   0.538 |    0.693 |
     | minmax_S3/U14/ZN          |  v   | minmax_S3/n6           | AOI222_X1                  | 0.046 |   0.584 |    0.739 |
     | minmax_S3/U15/C2          |  v   | minmax_S3/n6           | AOI222_X4                  | 0.000 |   0.584 |    0.739 |
     | minmax_S3/U15/ZN          |  ^   | minmax_S3/n22          | AOI222_X4                  | 0.159 |   0.743 |    0.898 |
     | minmax_S3/FE_DBTC0_n22/A  |  ^   | minmax_S3/n22          | INV_X1                     | 0.002 |   0.745 |    0.900 |
     | minmax_S3/FE_DBTC0_n22/ZN |  v   | minmax_S3/FE_DBTN0_n22 | INV_X1                     | 0.041 |   0.786 |    0.941 |
     | minmax_S3/U38/B2          |  v   | minmax_S3/FE_DBTN0_n22 | AOI22_X1                   | 0.000 |   0.786 |    0.942 |
     | minmax_S3/U38/ZN          |  ^   | out[2][5]              | AOI22_X1                   | 0.058 |   0.845 |    1.000 |
     | out[13]                   |  ^   | out[2][5]              | SortUnitStructRTL__nbits_8 | 0.000 |   0.845 |    1.000 |
     +---------------------------------------------------------------------------------------------------------------------+
...
```

This report is similar to the timing reports you saw in the previous
tutorial. Note that we can now see the clock network delay factored into
the beginning of the path. For paths that start at a register and end at
a register within the same design, we will see the clock network delay
factoted both at the beginning and end of the path. If these delays are
not equal we will have either positive or negative clock skew. The path
shown above is not between two registers, but is instead from a register
within the design to the output port. We have setup the tools so that
these paths must also be completed within one cycle. Note that there is
no clock network delay at the end of this path, because the end point is
an output port not a register. This might seem to penalize these REGOUT
paths, but keep in mind that there will be a register in the _next_
module which will have some setup time. So we will still end up with a
reasonable estimate even for REGOUT paths. The fanout and parasitic
capacitance on each net is also shown which can be useful in identifying
nets with unusually high loads. This critical path is similar but not
exactly the same as we saw in the previous tutorial. This is because the
ASIC flow uses more commands with different options than what we did
manually.

You can view the area report like this:

```
 % cd $TOPDIR/asic/build/pnr
 % less signoff.area.rpt

Hinst Name                 Module Name                         Inst Count           Total Area               Buffer             Inverter        Combinational                 Flop                Latch           Clock Gate                Macro             Physical
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
SortUnitStructRTL__nbits_8                                            332              701.176                0.000               43.092              210.406              447.678                0.000                0.000                0.000                0.000
 elm_S0S1__0               Reg__Type_Bits8_11                           8               36.176                0.000                0.000                0.000               36.176                0.000                0.000                0.000                0.000
 elm_S0S1__1               Reg__Type_Bits8_10                           8               36.176                0.000                0.000                0.000               36.176                0.000                0.000                0.000                0.000
 elm_S0S1__2               Reg__Type_Bits8_9                            8               36.176                0.000                0.000                0.000               36.176                0.000                0.000                0.000                0.000
 elm_S0S1__3               Reg__Type_Bits8_8                            8               36.176                0.000                0.000                0.000               36.176                0.000                0.000                0.000                0.000
 elm_S1S2__0               Reg__Type_Bits8_7                            8               36.176                0.000                0.000                0.000               36.176                0.000                0.000                0.000                0.000
 elm_S1S2__1               Reg__Type_Bits8_6                            8               36.176                0.000                0.000                0.000               36.176                0.000                0.000                0.000                0.000
 elm_S1S2__2               Reg__Type_Bits8_5                            8               36.176                0.000                0.000                0.000               36.176                0.000                0.000                0.000                0.000
 elm_S1S2__3               Reg__Type_Bits8_4                            8               36.176                0.000                0.000                0.000               36.176                0.000                0.000                0.000                0.000
 elm_S2S3__0               Reg__Type_Bits8_3                            8               36.176                0.000                0.000                0.000               36.176                0.000                0.000                0.000                0.000
 elm_S2S3__1               Reg__Type_Bits8_2                            8               36.176                0.000                0.000                0.000               36.176                0.000                0.000                0.000                0.000
 elm_S2S3__2               Reg__Type_Bits8_1                            8               36.176                0.000                0.000                0.000               36.176                0.000                0.000                0.000                0.000
 elm_S2S3__3               Reg__Type_Bits8_0                            8               36.176                0.000                0.000                0.000               36.176                0.000                0.000                0.000                0.000
 minmax0_S1                MinMaxUnit__nbits_8_4                       47               52.136                0.000                8.512               43.624                0.000                0.000                0.000                0.000                0.000
 minmax0_S2                MinMaxUnit__nbits_8_3                       47               52.136                0.000                8.512               43.624                0.000                0.000                0.000                0.000                0.000
 minmax1_S1                MinMaxUnit__nbits_8_2                       48               50.274                0.000                8.512               41.762                0.000                0.000                0.000                0.000                0.000
 minmax1_S2                MinMaxUnit__nbits_8_1                       48               50.274                0.000                8.512               41.762                0.000                0.000                0.000                0.000                0.000
 minmax_S3                 MinMaxUnit__nbits_8_0                       39               45.752                0.000                8.512               37.240                0.000                0.000                0.000                0.000                0.000
 val_S0S1                  RegRst__Type_Bits1__reset_value_0_2          3                5.852                0.000                0.532                0.798                4.522                0.000                0.000                0.000                0.000
 val_S1S2                  RegRst__Type_Bits1__reset_value_0_1          2                5.320                0.000                0.000                0.798                4.522                0.000                0.000                0.000                0.000
 val_S2S3                  RegRst__Type_Bits1__reset_value_0_0          2                5.320                0.000                0.000                0.798                4.522                0.000                0.000                0.000                0.000
```

This report is similar to what we saw in the previous tutorial. Note that
the total cell area is different from the total area. The total cell area
includes just the standard cells, while the total area includes the "Net
Interconnect Area". To be totally honest, I am not quite sure what "Net
Interconnect Area" actually means, but we use the total area in our
analysis. Again these numbers are not identical to the previous tutorial,
since the ASIC flow uses more commands with different options than what
we did manually.

We have written a little script to parse the reports and generate a
`summary.txt` file. This script takes care of looking across all four
path groups to fine the true cycle time that you should use in your
analysis.

```
 % cd $TOPDIR/asic/build/pnr
 % less summary.txt

#=========================================================================
# Post-Place-and-Route Results
#=========================================================================

design_name  = SortUnitStructRTL__nbits_8
design_area  = 701.176 um^2
stdcell_area = 701.176 um^2
macros_area  = 0.0 um^2
chip_area    = 1597.277 um^2
core_area    = 1006.544 um^2
target_clock = 1.0 ns
slack        = 0.155 ns
```

While we do not use GUIs to drive our flow, we often use GUIs to analyze
the results. You can start the Cadence Innovus GUI to visualize the final
layout like this:

```
 % cd $TOPDIR/asic/build/pnr
 % innovus -64
```

Once the GUI has finished loading you will viewing a "MainWindow", enter
`source save.enc` at the `innovus 1>` prompt to actually open up the most
recently placed-and-routed design in a "LayoutWindow".

As mentioned in the previous tutorial, we call the resulting plot an
"amoeba plot" because the tool often generates blocks that look like
amoebas. You can zoom in to see how the standard cells were placed and
how the routing was done. You can turn on an off the visibility of metal
layers using the panel on the right. One very useful feature is to view the
hierarchy and area breakdown. This will be critical for producing
high-quality amoeba plots. You can use the following steps to highlight
various modules on the amoeba plot:

 - Choose _Windows > Workspaces > Design Browser + Physical_ from the
 - menu Hide all of the metal layers by pressing the number keys Browse
 - the design hierarchy using the panel on the left Right click on a
 - module, click _Highlight_, select a color

Another very useful feature is to highlight the critical path on the
amoeba plot using the following steps:

 - Choose _Timing > Debug Timing_ from the menu
 - Right click on first path in the _Path List_
 - Choose _Highlight > Only This Path > Color_

You can see an example amoeba plot below. Note that you will need to use
some kind of "screen-capture" software to capture the plot.
You will also need to play with the colors to enable easily seeing
the various parts of your design.

![](assets/fig/sort-unit-amoeba-plot.png)

Using Synopsys PrimeTime for Power Analysis
--------------------------------------------------------------------------

We use Synopsys PrimeTime (PT) for power analysis. As described in the
previous tutorial, we are using an advanced form of power analysis which
combines activity factors from RTL simulation with the detailed
gate-level model. We can use `pyhflow` to run Synopsys PT like this:

```
 % cd $TOPDIR/asic/build
 % pyhflow run pwr
```

We have setup the flow to display the final summary information after
this step. You can also display it directly like this:

```
 % cd $TOPDIR/asic/build/pwr
 % less summary.txt

#=========================================================================
# Power & Energy Analysis Summary
#=========================================================================

design       = SortUnitStructRTL__nbits_8
exec_time    = 105 cycles
clock_period = 1.0 ns
power        = 1.455 mW
energy       = 0.152775 nJ
```

You can see the total area, cycle time, power, and energy for your design
when running the given input (i.e., when using the VCD file specified in
the `flow.py`). You can see an overview of the power consumption here:

```
 % cd $TOPDIR/asic/pwr
 % less power.rpt
 ...
                        Internal  Switching  Leakage    Total
Power Group             Power     Power      Power      Power   (     %)  Attrs
--------------------------------------------------------------------------------
clock_network           3.812e-04    0.0000    0.0000 3.812e-04 (24.79%)  i
register                4.263e-04 9.443e-05 7.829e-06 5.286e-04 (34.38%)
combinational           2.818e-04 3.385e-04 7.404e-06 6.277e-04 (40.83%)
sequential                 0.0000    0.0000    0.0000    0.0000 ( 0.00%)
memory                     0.0000    0.0000    0.0000    0.0000 ( 0.00%)
io_pad                     0.0000    0.0000    0.0000    0.0000 ( 0.00%)
black_box                  0.0000    0.0000    0.0000    0.0000 ( 0.00%)

  Net Switching Power  = 4.330e-04   (28.16%)
  Cell Internal Power  = 1.089e-03   (70.85%)
  Cell Leakage Power   = 1.523e-05   ( 0.99%)
                         ---------
Total Power            = 1.537e-03  (100.00%)
```

The sort unit consumes ~1.5mW of power when processing random input data.
This is in the same ballpark as we saw in the previous tutorial. These
numbers are not identical to the previous tutorial, since the ASIC flow
uses more commands with different options than what we did manually.
Power is the rate change of energy (i.e., energy divided by execution
time), so the total energy is just the product of the total power, the
number of cycles, and the cycle time. When we ran the sort unit simulator
at the beginning of the tutorial, we saw that the simulation required 105
cycles. Note that the summary from Synopsys PT reports 104 cycles. This
small discrepancy is just due to accounting (i.e., Synosys PT tries to
figure out the total number of cycles from the `.saif` file so sometimes
it is off by one). The cycle time is 1ns, so the total energy is
105x1.0x1.455 = 152.775pJ. Since we are doing 100 sorts, this corresponds to
about 1.53pJ per sort.

You can see a more detailed power breakdown by module here:

```
 % cd $TOPDIR/asic/pwr
 % less power.hierarchy.rpt
...
                                      Int      Switch   Leak      Total
Hierarchy                             Power    Power    Power     Power    %
--------------------------------------------------------------------------------
SortUnitStructRTL__nbits_8            1.09e-03 4.33e-04 1.52e-05  1.54e-03 100.0
  elm_S2S3__0 (Reg__Type_Bits8_3)     6.50e-05 1.54e-06 6.31e-07  6.72e-05   4.4
  elm_S1S2__0 (Reg__Type_Bits8_7)     6.57e-05 9.80e-06 6.33e-07  7.61e-05   5.0
  elm_S2S3__1 (Reg__Type_Bits8_2)     6.66e-05 1.20e-05 6.33e-07  7.92e-05   5.2
  val_S0S1 (RegRst__Type_Bits1__reset_value_0_2) 7.02e-06 6.21e-08 1.25e-07 7.21e-06   0.5
  elm_S1S2__1 (Reg__Type_Bits8_6)     6.27e-05 9.34e-06 6.32e-07  7.27e-05   4.7
  elm_S0S1__0 (Reg__Type_Bits8_11)    6.42e-05 9.67e-06 6.33e-07  7.45e-05   4.8
  elm_S2S3__2 (Reg__Type_Bits8_1)     6.70e-05 1.11e-05 6.33e-07  7.88e-05   5.1
  elm_S0S1__1 (Reg__Type_Bits8_10)    6.62e-05 6.66e-06 6.33e-07  7.35e-05   4.8
  minmax0_S1 (MinMaxUnit__nbits_8_4)  5.25e-05 5.92e-05 1.30e-06  1.13e-04   7.3
  elm_S2S3__3 (Reg__Type_Bits8_0)     6.24e-05 2.04e-06 6.32e-07  6.50e-05   4.2
  elm_S1S2__2 (Reg__Type_Bits8_5)     6.78e-05 7.86e-06 6.33e-07  7.63e-05   5.0
  elm_S0S1__2 (Reg__Type_Bits8_9)     6.67e-05 9.56e-06 6.33e-07  7.69e-05   5.0
  minmax0_S2 (MinMaxUnit__nbits_8_3)  5.35e-05 6.24e-05 1.30e-06  1.17e-04   7.6
  elm_S1S2__3 (Reg__Type_Bits8_4)     6.56e-05 7.32e-06 6.32e-07  7.35e-05   4.8
  elm_S0S1__3 (Reg__Type_Bits8_8)     6.71e-05 7.50e-06 6.33e-07  7.53e-05   4.9
  minmax1_S1 (MinMaxUnit__nbits_8_2)  5.15e-05 5.86e-05 1.27e-06  1.11e-04   7.2
  minmax1_S2 (MinMaxUnit__nbits_8_1)  4.80e-05 5.52e-05 1.25e-06  1.04e-04   6.8
  minmax_S3 (MinMaxUnit__nbits_8_0)   7.62e-05 1.03e-04 2.21e-06  1.81e-04  11.8
  val_S2S3 (RegRst__Type_Bits1__reset_value_0_0) 7.02e-06 2.09e-08 9.30e-08 7.13e-06   0.5
  val_S1S2 (RegRst__Type_Bits1__reset_value_0_1) 6.50e-06 3.52e-08 9.59e-08 6.64e-06   0.4
```

These results are similar to what we saw in the previous tutorial.

Using Verilog RTL Models
--------------------------------------------------------------------------

TBD

Using the Automated ASIC Flow for Design-Space Exploration
--------------------------------------------------------------------------

One of the key benefits of using an automated ASIC flow is that it
enables rapid design space exploration of different clock constraints,
input datasets, and design configurations. In this section, we will
briefly conduct three different experiments: (1) pushing the sort unit to
run at a faster clock frequency, (2) exploring the impact different input
datasets can have on power consumption, and (3) comparing the pipelined
sort unit to an unpipelined sort unit. This section will be working with
the PyMTL RTL implementation, so if you attempted to push the Verilog RTL
implementation in the previous section, we need to go back and regenerate
the Verilog from the PyMTL RTL implementation. Of course, you should also
feel free to try out these ideas using the Verilog RTL implementation.

```
 % cd $TOPDIR/sim/build
 % rm -rf *
 % ../tut3_pymtl/sort/sort-sim --impl rtl-struct --translate --dump-vcd
```

Recall that the sort unit had no problem meeting the 1ns clock
constraint. We usually want to push our designs until there is a couple
of percent negative slack (e.g., less than 5%) to ensure we are
accurately estimating the true peak performance of our design. So let's
push the sort unit through the flow again with a clock constraint of
0.95ns. You need to modify the `flow.py` as follows:

```
 % cd $TOPDIR/asic/build
 % less flow.py

#-------------------------------------------------------------------------
# Flow parameters
#-------------------------------------------------------------------------

build_dir = '../../../sim/build'
files = [
  f'{build_dir}/SortUnitStructRTL__nbits_8__pickled.v',
  f'{build_dir}/sort-rtl-struct-random.verilator1.vcd',
]
top_name   = 'SortUnitStructRTL__nbits_8'
clk_period = 0.95 #ns
```

Then simply use `pyhflow` to reconfigure and rerun all the steps again.
We have added a `summary` step in the end that parses the area, timing,
and power reports for you and prints out useful information. You can
run the `summary` step as follow:

```
 % cd $TOPDIR/asic/build
 % pyhflow configure
 % pyhflow run summary

==========================================================================
 Summary
==========================================================================

design_name   = SortUnitStructRTL__nbits_8
design_area   = 707.294 um^2
stdcells_area = 707.294 um^2
macros_area   = 0.0 um^2
chip_area     = 1612.066 um^2
core_area     = 1018.248 um^2
constraint    = 0.95 ns
slack         = 0.164 ns
actual_clk    = 0.786 ns
exec_time     = 105 cycles
power         = 1.474 mW
energy        = 0.147031 nJ
```

The summary is also saved to `summary.txt` in the `summary` directory.
You can access it like this:

```
% cd $TOPDIR/asic/build/summary
$ less summary.txt
```

Recall that earlier in the tutorial, we used a clock cycle constraint of
1ns and we had 0.02ns of positive slack. With a clock cycle constraint of
0.95ns we have 0.01ns of positive slack. This means the tools are still
meeting the clock constraint, but the positive slack is getting very
small meaning we are starting to approach the limit of how fast the sort
unit can run. The automated ASIC flow makes it relatively easy to
continue to push the design a bit. Here are the results for a variety of
different experiments with gradually decreasing clock constraints.

| clk (ns) | slack (ns) | ctime (ns) | area (um^2) | power (mW) |
|----------|------------|------------|-------------|------------|
| 1.00     |  0.155     | 0.845      | 701         |  1.45      |
| 0.95     |  0.164     | 0.786      | 707         |  1.46      |
| 0.90     |  0.08      | 0.820      | 711         |  1.44      |
| 0.85     |  0.15      | 0.700      | 720         |  1.44      |
| 0.80     |  0.14      | 0.660      | 735         |  1.47      |
| 0.75     |  0.082     | 0.668      | 826         |  1.57      |
| 0.70     |  0.176     | 0.524      | 734         |  1.40      |
| 0.65     |  0.181     | 0.469      | 736         |  1.39      |
| 0.60     |  0.126     | 0.474      | 737         |  1.39      |
| 0.55     |  0.113     | 0.437      | 732         |  1.39      |
| 0.50     |  0.067     | 0.433      | 734         |  1.39      |
| 0.45     |  0.046     | 0.414      | 736         |  1.40      |
| 0.40     |  0.009     | 0.391      | 799         |  1.64      |
| 0.35     |  0.002     | 0.348      | 972         |  2.05      |
| 0.30     |  -0.022    | 0.322      | 916         |  1.96      |
| 0.25     |  -0.065    | 0.315      | 1001        |  2.32      |
| 0.20     |  -0.114    | 0.314      | 994         |  2.30      |

where `clk` is the clock constraint, and `ctime` is the cycle time. So we
can make a couple important observations. First, as we decrease the clock
constraint, the area and power generally increase. This is to be expected
since a more aggressive clock constraint requires the tools to use larger
cells and potentially more sophisticated logic implementations. In
addition, a more aggressive clock constraint results in a shorter cycle
time (higher clock frequency) which also increases the power. If we just
take these results on face value, then it appears the optimum cycle time
is approximately ~0.65ns. However, we can only achieve this cycle time by
pushing the tools with a clock cycle constraint less than 0.65ns. Notice
that with these lower clock constraints, the negative slack begins to
become a significant percentage of the clock constraint. We need to be
careful because if you push the tools too hard: (1) they can take forever
to finish, and (2) they can produce incorrect results. If the tools have
troubling placing and/or routing the design without causing very large
negative slack, they may just give up. I doubt the design produced with a
clock constraint of 0.2ns would actually work at all. In general, we
recommend shooting for about 10-20% negative slack. This should give very
reasonable results. You _definitely_ do not need to do so many
experiments. Just start with a reasonable clock cycle constraint, and
then maybe try another one or two constraints to find a reasonable
design. So for this example, we will choose a clock constraint of 0.55ns
since this achieves a good cycle time without too much negative slack.
Alternatively, if you are comparing multiple designs, sometimes the best
situation is to tune the baseline so it has a couple of percent of
negative slack and then ensure the alternative designs have similar cycle
times. This will enable a fair comparison since all designs will be
running at the same cycle time.

Note that the above data suggests the sort unit will consume ~12mW of
power when using a clock constraint of 0.55ns and processing random input
data. With a cycle time of 0.66ns, the total energy is 104x0.66x12 =
823pJ or 8.2pJ per sort. Let's do a quick experiment to compare the
energy for sorting a stream of all zeros to the energy for sorting a
stream of random values. We do _not_ need to re-synthesize and
re-place-and-route the design. We just need to generate a new VCD file
and re-run Synopsys PT. So first we re-run the sort unit simulator with a
different input:

```
 % cd $TOPDIR/sim/build
 % ../tut3_pymtl/sort/sort-sim --impl rtl-struct --stats --input zeros --translate --dump-vcd
```

Now we need to change the entry in the `flow.py` to point to the new VCD
file. The entry in the `flow.py` should look like this:

```
 % cd $TOPDIR/asic/build
 % less flow.py

build_dir = '../../../sim/build'
files = [
  f'{build_dir}/SortUnitStructRTL__nbits_8__pickled.v',
  f'{build_dir}/sort-rtl-struct-zeros.verilator1.vcd',
]

```

Now we re-run Synopsys PT:

```
 % cd $TOPDIR/asic/build
 % pyhflow configure
 % pyhflow run pwr

...
#=========================================================================
# Power & Energy Analysis Summary
#=========================================================================

design       = SortUnitStructRTL__nbits_8
exec_time    = 105 cycles
clock_period = 1.0 ns
power        = 0.7033 mW
energy       = 0.0738465 nJ
```

Not surprisingly, sorting a stream of zeros consumes significantly less
energy compared to sorting a stream of random values: 154pJ vs 74pJ. One
might ask why the sort unit consumes _any_ energy if it is just sorting a
stream of zeros. We can dig into the report to find the answer:

```
 % cd $TOPDIR/asic/build/pwr
 % less power.hierarchy.rpt
...
                                      Int      Switch   Leak      Total
Hierarchy                             Power    Power    Power     Power    %
--------------------------------------------------------------------------------
SortUnitStructRTL__nbits_8            6.88e-04 1.20e-07 1.49e-05  7.03e-04 100.0
  elm_S2S3__0 (Reg__Type_Bits8_3)     5.56e-05    0.000 6.08e-07  5.63e-05   8.0
  elm_S1S2__0 (Reg__Type_Bits8_7)     5.56e-05    0.000 6.08e-07  5.63e-05   8.0
  elm_S2S3__1 (Reg__Type_Bits8_2)     5.56e-05    0.000 6.08e-07  5.63e-05   8.0
  val_S0S1 (RegRst__Type_Bits1__reset_value_0_2) 7.03e-06 6.43e-08 1.25e-07 7.21e-06   1.0
  elm_S1S2__1 (Reg__Type_Bits8_6)     5.56e-05    0.000 6.08e-07  5.63e-05   8.0
  elm_S0S1__0 (Reg__Type_Bits8_11)    5.56e-05    0.000 6.08e-07  5.63e-05   8.0
  elm_S2S3__2 (Reg__Type_Bits8_1)     5.56e-05    0.000 6.08e-07  5.63e-05   8.0
  elm_S0S1__1 (Reg__Type_Bits8_10)    5.56e-05    0.000 6.08e-07  5.63e-05   8.0
  minmax0_S1 (MinMaxUnit__nbits_8_4)     0.000    0.000 1.46e-06  1.46e-06   0.2
  elm_S2S3__3 (Reg__Type_Bits8_0)     5.56e-05    0.000 6.08e-07  5.63e-05   8.0
  elm_S1S2__2 (Reg__Type_Bits8_5)     5.56e-05    0.000 6.08e-07  5.63e-05   8.0
  elm_S0S1__2 (Reg__Type_Bits8_9)     5.56e-05    0.000 6.08e-07  5.63e-05   8.0
  minmax0_S2 (MinMaxUnit__nbits_8_3)     0.000    0.000 1.46e-06  1.46e-06   0.2
  elm_S1S2__3 (Reg__Type_Bits8_4)     5.56e-05    0.000 6.08e-07  5.63e-05   8.0
  elm_S0S1__3 (Reg__Type_Bits8_8)     5.56e-05    0.000 6.08e-07  5.63e-05   8.0
  minmax1_S1 (MinMaxUnit__nbits_8_2)     0.000    0.000 1.48e-06  1.48e-06   0.2
  minmax1_S2 (MinMaxUnit__nbits_8_1)     0.000    0.000 1.50e-06  1.50e-06   0.2
  minmax_S3 (MinMaxUnit__nbits_8_0)      0.000    0.000 1.34e-06  1.34e-06   0.2
  val_S2S3 (RegRst__Type_Bits1__reset_value_0_0) 7.02e-06 1.90e-08 9.30e-08 7.13e-06   1.0
  val_S1S2 (RegRst__Type_Bits1__reset_value_0_1) 6.51e-06 3.66e-08 9.59e-08 6.64e-06   0.9
```

Notice that the switching power is indeed zero for the pipeline
registers, but not the valid bit. This is probably because the valid bit
does toggle at the beginning and end of the simulation; the absolute
switching power of valid bit is very, very small. Notice that there is
still leakage, but none of this accounts for the majority of the 275pJ.
The key is the internal power of the pipeline registers. Internal power
also includes the clock power for sequential state elements, so
effectively while sorting a stream of zeros results in very little energy
on the data bits we still require energy to toggle the clock across all
of the pipeline registers. In this design there are 12 8-bit pipeline
registers which is quite a bit of state. So the key point here is that we
want to always try small experiments to verify that things are working as
expected, and that you will almost certainly need to dig into the
detailed reports to understand what is going on.

Our final experiment will focus on the effect of removing the pipeline
registers to transform our three-stage pipelined sort unit into a
single-stage unpipelined sort unit. Essentially we want to implement the
following design.

![](assets/fig/sort-unit-scycle-dpath.png)

Go ahead and remove the pipeline registers in `SortUnitStructRTL.py`.
Remember to modify the `line_trace` function and remove the line trace
of the pipeline register as well.

```
  def line_trace( s ):

    def trace_val_elm( val, elm ):
      str_ = f"{elm[0]},{elm[1]},{elm[2]},{elm[3]}"
      if not val:
        str_ = ' '*len(str_)
      return str_

    return "{}|{}".format(
      trace_val_elm( s.in_val,        s.in_                         ),
      trace_val_elm( s.out_val,       s.out                         ),
    )
```

Then modify the tests in `SortUnitStructRTL_test.py` so that they
correctly test for single-cycle behavior. Here is an example of the how
you might want to modify your tests.

```
def test_basic( dump_vcd, test_verilog ):
  run_test_vector_sim( SortUnitStructRTL(), [ header_str,
    # in  in  in  in  in  out out out out out
    # val [0] [1] [2] [3] val [0] [1] [2] [3]
    [ 0,  0,  0,  0,  0,  0,  x,  x,  x,  x ],
    [ 1,  4,  2,  3,  1,  0,  x,  x,  x,  x ],
    [ 0,  0,  0,  0,  0,  1,  1,  2,  3,  4 ],
    [ 0,  0,  0,  0,  0,  0,  x,  x,  x,  x ],
  ], dump_vcd, test_verilog )

...

def test_stream( dump_vcd, test_verilog ):
  run_test_vector_sim( SortUnitStructRTL(), mk_test_vector_table( 1, [
    [ 4, 3, 2, 1 ], [ 9, 6, 7, 1 ], [ 4, 8, 0, 9 ]
  ]), dump_vcd, test_verilog )
```

Notice how we use 1 instead of 3 as the first parameter to
`mk_test_vector_table`. This will enable the helper function to correctly
generate the reference outputs assuming a single-cycle sort unit. Make
sure your new design passes the tests and use line tracing to confirm
proper single-cycle behavior.

```
 % cd $TOPDIR/sim/build
 % pytest ../tut3_pymtl/sort
 % pytest ../tut3_pymtl/sort/SortUnitStructRTL_test.py -k basic -s
 ../tut3_pymtl/sort/test/SortUnitStructRTL_test.py
...
../tut3_pymtl/sort/test/SortUnitStructRTL_test.py
  1r            |
  2r            |
  3:            |
  4: 04,02,03,01|
  5:            |01,02,03,04
  6:            |
  7:            |
  8:            |
  9:            |
``

Once we know the single-cycle unpipelined sort unit is correct, we can
test Verilog translation and use the simulator to generate the new
Verilog RTL and VCD file for the ASIC flow.

``
 % pytest ../tut3_pymtl/sort --test-verilog
 % ../tut3_pymtl/sort/sort-sim --impl rtl-struct --translate --dump-vcd --stats

num_cycles          = 104
num_cycles_per_sort = 1.04
```

Make sure you modify the `flow.py` to reference the random VCD file,
since that is what we just generated using the sort unit simulator. Let's
also start with a clock constraint of 0.5ns.

```
 % cd $TOPDIR/asic/build
 % less flow.py

...
#-------------------------------------------------------------------------
# Flow parameters
#-------------------------------------------------------------------------

build_dir = '../../../sim/build'
files = [
  f'{build_dir}/SortUnitStructRTL__nbits_8__pickled.v',
  f'{build_dir}/sort-rtl-struct-random.verilator1.vcd',
]
top_name   = 'SortUnitStructRTL__nbits_8'
clk_period = 0.5 #ns
...
```

We are now ready to push the single-cycle unpipelined sort unit through
the flow.

```
 % cd $TOPDIR/asic/build
 % pyhflow configure
 % pyhflow run
...
#=========================================================================
# Post-Place-and-Route Results
#=========================================================================

design_name  = SortUnitStructRTL__nbits_8
design_area  = 636.804 um^2
stdcell_area = 636.804 um^2
macros_area  = 0.0 um^2
chip_area    = 1177.529 um^2
core_area    = 679.896 um^2
target_clock = 0.5 ns
slack        = -0.166 ns
...
```

Not surprisingly, the tools cannot meet the same clock constraint that we
used with the three-stage pipelined sort unit (there is simply too much
logic per stage). We have a negative slack of about 30% of the clock
constraint, so this is not too bad of a design point. The resulting cycle
time is 0.666ns. The three-stage pipelined design had a cycle time of
0.315ns, so we might expect the single-cycle unpipelined design to have a
cycle time of 0.945ns. Digging into the timing reports helps explain what
is going on.

