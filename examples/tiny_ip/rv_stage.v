// Single-entry ready/valid pipeline stage used solely for skill demonstration.
module rv_stage #(
    parameter WIDTH = 8
) (
    input  wire             clk,
    input  wire             rst_n,
    input  wire [WIDTH-1:0] in_data,
    input  wire             in_valid,
    output wire             in_ready,
    output reg  [WIDTH-1:0] out_data,
    output reg              out_valid,
    input  wire             out_ready
);

    assign in_ready = ~out_valid | out_ready;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            out_valid <= 1'b0;
            out_data  <= {WIDTH{1'b0}};
        end else if (in_ready) begin
            out_valid <= in_valid;
            if (in_valid)
                out_data <= in_data;
        end
    end
endmodule
