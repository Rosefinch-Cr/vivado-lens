// Testbench for alu8
`timescale 1ns/1ps

module tb_alu8;

    reg        clk = 0;
    reg        rst_n = 0;
    reg  [7:0] a = 0;
    reg  [7:0] b = 0;
    reg  [2:0] op = 0;
    wire [7:0] result;
    wire       zero, negative, carry;

    integer pass_count = 0;
    integer fail_count = 0;

    alu8 uut (
        .clk(clk), .rst_n(rst_n),
        .a(a), .b(b), .op(op),
        .result(result), .zero(zero), .negative(negative), .carry(carry)
    );

    always #5 clk = ~clk;  // 100 MHz

    task apply_and_check;
        input [7:0] ta, tb_in;
        input [2:0] top;
        input [7:0] expected;
        input       expect_carry;
        input [127:0] label;
        begin
            @(negedge clk);
            a = ta; b = tb_in; op = top;
            @(posedge clk); #1;  // wait one clock + small delta
            @(posedge clk); #1;  // wait flag update
            if (result === expected && (top > 3'b001 || carry === expect_carry)) begin
                $display("PASS: %s  a=%h b=%h op=%b -> result=%h carry=%b zero=%b neg=%b",
                         label, ta, tb_in, top, result, carry, zero, negative);
                pass_count = pass_count + 1;
            end else begin
                $display("FAIL: %s  a=%h b=%h op=%b -> result=%h (expected %h) carry=%b",
                         label, ta, tb_in, top, result, expected, carry);
                fail_count = fail_count + 1;
            end
        end
    endtask

    initial begin
        $display("=== ALU8 Testbench Start ===");
        rst_n = 0;
        repeat(2) @(posedge clk);
        rst_n = 1;
        @(posedge clk);

        apply_and_check(8'h0A, 8'h05, 3'b000, 8'h0F, 1'b0, "ADD basic");
        apply_and_check(8'hFF, 8'h01, 3'b000, 8'h00, 1'b1, "ADD overflow");
        apply_and_check(8'h10, 8'h03, 3'b001, 8'h0D, 1'b0, "SUB basic");
        apply_and_check(8'h00, 8'h01, 3'b001, 8'hFF, 1'b1, "SUB borrow");
        apply_and_check(8'hF0, 8'h0F, 3'b010, 8'h00, 1'b0, "AND  ");
        apply_and_check(8'hF0, 8'h0F, 3'b011, 8'hFF, 1'b0, "OR   ");
        apply_and_check(8'hAA, 8'h55, 3'b100, 8'hFF, 1'b0, "XOR  ");
        apply_and_check(8'h81, 8'h00, 3'b101, 8'h02, 1'b0, "SHL  ");
        apply_and_check(8'h81, 8'h00, 3'b110, 8'h40, 1'b0, "SHR  ");
        apply_and_check(8'h0F, 8'h00, 3'b111, 8'hF0, 1'b0, "NOT  ");

        $display("=== Summary: %0d PASS, %0d FAIL ===", pass_count, fail_count);
        if (fail_count == 0)
            $display("PASS: All %0d tests passed!", pass_count);
        else
            $display("FAIL: %0d tests failed", fail_count);

        $finish;
    end

    initial begin
        #1000;
        $display("FAIL: Timeout");
        $finish;
    end

endmodule
