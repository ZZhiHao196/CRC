module reverse_bits #( parameter bits = 8)(
    input [bits-1:0] data,
    output reg [bits-1:0] reversed_data
);

integer i;

always @(*) begin
    reversed_data=0;
    for (i=0;i<bits;i=i+1) begin
        reversed_data = reversed_data|(data[i]<<(bits-1-i));
    end
end
endmodule