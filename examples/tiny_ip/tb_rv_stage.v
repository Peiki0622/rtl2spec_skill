`timescale 1ns/1ps
module tb_rv_stage;
    reg clk = 0;
    reg rst_n = 0;
    reg in_valid = 0;
    reg [7:0] in_data = 0;
    wire in_ready;
    wire [7:0] out_data;
    wire out_valid;
    reg out_ready = 0;

    rv_stage #(.WIDTH(8)) dut (
        .clk(clk), .rst_n(rst_n), .in_valid(in_valid), .in_data(in_data),
        .in_ready(in_ready), .out_valid(out_valid), .out_ready(out_ready)
    );
    always #5 clk = ~clk;
    initial begin
        $dumpfile("rv_stage.vcd");
        $dumpvars(0, tb_rv_stage);
        #12 rst_n = 1;
        #1  in_valid = 1; in_data = 8'hA5;
        #7  in_data = 8'h3C;  // t20: first item is stalled
        #10 out_ready = 1;   // t30: replace output at t35
        #10 in_valid = 0;   // t40: drain at t45
        #20 $finish;
    end
endmodule
