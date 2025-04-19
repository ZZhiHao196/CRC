module crc_process_byte #(
    parameter bits     = 8,
    parameter poly     = 8'h33
)
(
    input  refin_in,
    input  [8-1:0] byte_in,
    input  [bits-1:0] crc_in,
    output  reg [bits-1:0] crc_out
);

reg [7:0] byte_reg;
reg [bits-1:0] crc_reg;

integer i;

always@(*)begin
    byte_reg = refin_in? reflect(byte_in): byte_in;
    crc_reg =crc_in^(byte_reg<<(bits-8));
    crc_out =0;
    for(i=0;i<8;i=i+1)begin
        if(crc_reg[bits-1])begin
            crc_reg=((crc_reg<<1)^poly)&((1<<bits)-1);
        end
        else begin
            crc_reg=(crc_reg<<1)&((1<<bits)-1);
        end
    end
    crc_out =crc_reg;
end


// 位翻转函数实现
    function [7:0] reflect;
        input [7:0] data;
        integer i;
        begin
            reflect = 0;
            for (i = 0; i < 8; i = i + 1)
                reflect = reflect|(data[i]<<(7-i));
        end
    endfunction

endmodule
