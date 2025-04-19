`timescale 1ns/1ns

// CRC配置选择
`define Crc_Standard 1
// `define Crc_Mixed1 1
// `define Crc_Mixed2 1
// `define Crc_Reverse 1

// 根据选择包含对应配置文件
`ifdef Crc_Standard
  `include "../settings/crc_config_1.vh"
`elsif Crc_Mixed1
  `include "../settings/crc_config_2.vh"
`elsif Crc_Mixed2
  `include "../settings/crc_config_3.vh"
`elsif Crc_Reverse
  `include "../settings/crc_config_4.vh"
`endif

// 包含CRC核心模块
`include "../src/crc.v"

module crc_tb;
    // 信号声明
    reg clk;
    reg rst_n;
    reg data_valid;
    reg start;
    reg [7:0] data_in;
    wire crc_ready;
    wire [`CRC_WIDTH-1:0] crc_out;
    
    // 文件处理
    integer input_file; // 输入文件
    integer output_file; // 输出文件
    integer scan_result; // 扫描结果
    
    // 测试数据存储
    integer data_length; // 数据长度
    reg [7:0] test_data [0:1023]; // 支持最多1024字节的测试数据
    integer i; // 循环计数器
    integer j; // 数据读取循环计数器
    integer max_tests = 4; // 最大测试数量
    reg [8*100:1] input_filename; // 输入文件名
    reg [8*100:1] output_filename; // 输出文件名
    reg valid_test; // 测试有效标志
    
    // 直接实例化CRC模块，不再使用crc_top作为中间层
    crc #(
        .bits(`CRC_WIDTH),
        .poly(`CRC_POLY),
        .init(`CRC_INIT),
        .refin(`CRC_REFIN),
        .refout(`CRC_REFOUT),
        .xorout(`CRC_XOROUT)
    ) crc_inst (
        .clk(clk),
        .rst_n(rst_n),
        .data_valid(data_valid),
        .start(start),
        .data_in(data_in),
        .crc_ready(crc_ready),
        .crc_out(crc_out)
    );
    
    // 时钟生成
    initial begin
        clk = 0;
        forever #5 clk = ~clk; // 10ns周期时钟
    end
    
    // 波形文件设置
    initial begin
        $dumpfile("crc_test.vcd");
        $dumpvars(0, crc_tb);
    end
    
    // 测试过程
    initial begin
        // 确定当前使用的配置
        $display("========= CRC配置信息 =========");
        
        // 简化的配置显示
        `ifdef Crc_Standard
            $display("当前使用: 标准模式");
        `endif
        
        `ifdef Crc_Mixed1
            $display("当前使用: 混合模式一");
        `endif
        
        `ifdef Crc_Mixed2
            $display("当前使用: 混合模式二");
        `endif
        
        `ifdef Crc_Reverse
            $display("当前使用: 反转模式");
        `endif
        
        $display("CRC宽度: %0d", `CRC_WIDTH);
        $display("CRC多项式: 0x%h", `CRC_POLY);
        $display("初始值: 0x%h", `CRC_INIT);
        $display("输入反转: %0d", `CRC_REFIN);
        $display("输出反转: %0d", `CRC_REFOUT);
        $display("结果异或值: 0x%h", `CRC_XOROUT);
        $display("===============================");
        
        // 循环处理每个测试文件
        for (i = 1; i <= max_tests; i = i + 1) begin
            valid_test = 1; // 初始假设测试有效
            
            // 构建文件名
            `ifdef Crc_Standard
                $sformat(input_filename, "../../dataset/Test_Model/input/test_data_c1_t%0d_input.dat", i);
                $sformat(output_filename, "../../dataset/Test_Model/rtl_data/test_data_c1_t%0d_output.dat", i);
            `elsif Crc_Mixed1
                $sformat(input_filename, "../../dataset/Test_Model/input/test_data_c2_t%0d_input.dat", i);
                $sformat(output_filename, "../../dataset/Test_Model/rtl_data/test_data_c2_t%0d_output.dat", i);
            `elsif Crc_Mixed2
                $sformat(input_filename, "../../dataset/Test_Model/input/test_data_c3_t%0d_input.dat", i);
                $sformat(output_filename, "../../dataset/Test_Model/rtl_data/test_data_c3_t%0d_output.dat", i);
            `elsif Crc_Reverse
                $sformat(input_filename, "../../dataset/Test_Model/input/test_data_c4_t%0d_input.dat", i);
                $sformat(output_filename, "../../dataset/Test_Model/rtl_data/test_data_c4_t%0d_output.dat", i);
            `endif
            
            // 打开测试数据文件
            input_file = $fopen(input_filename, "r");
            if (input_file == 0) begin
                $display("注意: 文件 %s 不存在或无法打开，跳过", input_filename);
                valid_test = 0; // 标记测试无效
            end
            
            if (valid_test) begin
                $display("\n===== 处理测试 #%0d =====", i);
                $display("输入文件: %s", input_filename);
                
                // 读取数据长度
                scan_result = $fscanf(input_file, "%d", data_length);
                if (scan_result != 1) begin
                    $display("错误: 无法读取数据长度");
                    $fclose(input_file);
                    valid_test = 0; // 标记测试无效
                end
            end
            
            if (valid_test) begin
                // 读取数据字节
                j = 0;
                valid_test = 1; // 重置有效标志
                
                while (j < data_length && valid_test) begin
                    scan_result = $fscanf(input_file, "%h", test_data[j]);
                    if (scan_result != 1) begin
                        $display("错误: 无法读取字节 %d", j);
                        valid_test = 0; // 标记测试无效
                    end else begin
                        j = j + 1;
                    end
                end
                
                // 关闭输入文件
                $fclose(input_file);
            end
            
            if (valid_test) begin
                // 开始CRC计算
                $display("数据长度: %d 字节", data_length);
                
                // 初始化信号
                rst_n = 0;
                data_valid = 0;
                start = 0;
                data_in = 0;
                
                // 重置CRC模块
                #20;
                rst_n = 1;
                #20;
                
                // 开始新的CRC计算
                start = 1;
                #10;
                start = 0;
                
                // 发送测试数据
                for (j = 0; j < data_length; j = j + 1) begin
                    data_in = test_data[j];
                    data_valid = 1;
                    #10;
                end
                
                // 停止数据输入，等待结果
                data_valid = 0;
                
                // 等待CRC计算完成
                wait(crc_ready);
                #10;
                
                // 显示结果
                $display("CRC结果: 0x%h", crc_out);
                
                // 保存结果到输出文件
                output_file = $fopen(output_filename, "w");
                if (output_file == 0) begin
                    $display("错误: 无法打开输出文件 %s", output_filename);
                end else begin
                    // 以十六进制格式写入CRC结果
                    $fdisplay(output_file, "%h", crc_out);
                    // 关闭输出文件
                    $fclose(output_file);
                    $display("结果已保存到: %s", output_filename);
                end
            end
        end
        
        $display("\n测试完成");
        $finish;
    end
    
endmodule