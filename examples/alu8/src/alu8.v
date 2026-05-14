// 8-bit ALU with flags
// Operations:
//   3'b000: ADD  (a + b)
//   3'b001: SUB  (a - b)
//   3'b010: AND  (a & b)
//   3'b011: OR   (a | b)
//   3'b100: XOR  (a ^ b)
//   3'b101: SHL  (a << 1)
//   3'b110: SHR  (a >> 1)
//   3'b111: NOT  (~a)
// Flags: zero (result == 0), negative (result[7]), carry (ADD/SUB only)

module alu8 (
    input  wire        clk,
    input  wire        rst_n,
    input  wire [7:0]  a,
    input  wire [7:0]  b,
    input  wire [2:0]  op,
    output reg  [7:0]  result,
    output reg         zero,
    output reg         negative,
    output reg         carry
);

    reg [8:0] tmp;  // 9-bit for carry detection

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            result   <= 8'h00;
            zero     <= 1'b0;
            negative <= 1'b0;
            carry    <= 1'b0;
        end else begin
            carry <= 1'b0;
            case (op)
                3'b000: begin
                    tmp     = {1'b0, a} + {1'b0, b};
                    result <= tmp[7:0];
                    carry  <= tmp[8];
                end
                3'b001: begin
                    tmp     = {1'b0, a} - {1'b0, b};
                    result <= tmp[7:0];
                    carry  <= tmp[8];   // borrow
                end
                3'b010: result <= a & b;
                3'b011: result <= a | b;
                3'b100: result <= a ^ b;
                3'b101: result <= a << 1;
                3'b110: result <= a >> 1;
                3'b111: result <= ~a;
            endcase

            zero     <= (result == 8'h00);
            negative <= result[7];
        end
    end

endmodule
