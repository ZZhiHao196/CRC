`include "crc_process_byte.v"
module crc #(
    parameter bits =8,
    parameter poly =8'h33,
    parameter init =8'hff,
    parameter [0:0]refin =1'b0,
    parameter [0:0]refout =1'b0,
    parameter xorout =8'h00
)(
    input clk,
    input rst_n,
    input data_valid,
    input start,
    input [7:0] data_in,
    output reg crc_ready,
    output reg [bits-1:0] crc_out
);

// 内部寄存器
reg  [bits-1:0] crc_reg;
wire [bits-1:0] crc_next;
reg data_processed;  // 添加标志，指示是否有数据被处理过

//实列化字节处理模块
crc_process_byte #(.bits(bits),.poly(poly)) uut (
    .crc_in(crc_reg),
    .byte_in(data_in),
    .refin_in(refin),
    .crc_out(crc_next)
);

// 位翻转函数实现
    function [bits-1:0] reflect;
        input [bits-1:0] data;
        integer i;
        begin
            reflect = 0;
            for (i = 0; i < bits; i = i + 1)
                reflect = reflect|(data[i]<<(bits-1-i));
        end
    endfunction

always @(posedge clk or negedge rst_n) begin
    if(!rst_n) begin
        crc_reg <= init;
        crc_ready <= 0;
        crc_out <= 0;
        data_processed <= 0;
    end else if(start) begin
        // 开始新的计算
        crc_reg <= init;
        crc_ready <= 0;
        data_processed <= 0;
    end else if(data_valid) begin
        // 处理数据
        crc_reg <= crc_next;
        crc_ready <= 0;  // 数据处理中，结果未就绪
        data_processed <= 1;  // 标记已处理数据
    end else if (data_processed && !data_valid && !crc_ready) begin
        // 数据处理完成：已经处理过数据，当前无更多数据，结果未就绪
        if(refout) begin
            crc_out <= (reflect(crc_reg) ^ xorout) & ((1<<bits)-1);
        end else begin
            crc_out <= (crc_reg ^ xorout) & ((1<<bits)-1);
        end
        crc_ready <= 1;  // 结果就绪
    end
end

endmodule