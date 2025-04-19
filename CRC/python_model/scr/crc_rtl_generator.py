"""
RTL硬件CRC配置和测试数据生成器
"""
import os
import random
import argparse
import json
from pathlib import Path

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='生成硬件RTL CRC配置和测试数据')
    parser.add_argument('--n-configs', type=int, default=1, 
                      help='每种反转类型的配置数量')
    parser.add_argument('--n-tests', type=int, default=4, 
                      help='每个配置要生成的测试数量')
    parser.add_argument('--min-length', type=int, default=3, 
                      help='测试数据最小长度(字节)')
    parser.add_argument('--max-length', type=int, default=20, 
                      help='测试数据最大长度(字节)')
    parser.add_argument('--seed', type=int, default=None, 
                      help='随机数种子(可选)')
    parser.add_argument('--output-dir', type=str, default='./dataset/Test_Model/input', 
                      help='输出目录')
    return parser.parse_args()

def generate_polynomial(width):
    """生成随机CRC多项式"""
    # 确保多项式的最高位和最低位始终为1
    poly = (1 << width) | 1
    
    # 随机设置其他位
    for i in range(1, width):
        if random.random() > 0.5:
            poly |= (1 << i)
    
    return poly

def generate_hardware_config(config_type):
    """生成特定类型的硬件CRC配置"""
    common_widths = [8, 16, 32]
    width = random.choice(common_widths)
    
    polynomial = generate_polynomial(width)
    
    # 使用所有位为1的初始值
    init = (1 << width) - 1  # 如0xFF, 0xFFFF, 0xFFFFFFFF
    
    # 基本配置
    config = {
        "width": width,
        "poly": polynomial,
        "init": init,
        "xorout": 0,  # 通常为0
    }
    
    # 根据配置类型设置反转参数
    if config_type == "standard":
        config["refin"] = False
        config["refout"] = False
        config["type_name"] = "standard"
    elif config_type == "mixed_one":
        config["refin"] = True
        config["refout"] = False
        config["type_name"] = "mixed_one"
    elif config_type == "mixed_two":
        config["refin"] = False
        config["refout"] = True
        config["type_name"] = "mixed_two"
    elif config_type == "reflect":
        config["refin"] = True
        config["refout"] = True
        config["type_name"] = "reflect"
    
    return config

def save_rtl_config(config, config_id, rtl_dir):
    """保存RTL配置为Verilog头文件"""
    rtl_path = os.path.join(rtl_dir, f"crc_config_{config_id}.vh")
    with open(rtl_path, 'w') as f:
        f.write("// 自动生成的CRC配置文件\n")
        f.write(f"// 配置类型: {config['type_name']}\n\n")
        f.write(f"`define CRC_WIDTH 'd{config['width']}\n")
        f.write(f"`define CRC_POLY 'h{config['poly']:x}\n")
        f.write(f"`define CRC_INIT 'h{config['init']:x}\n")
        f.write(f"`define CRC_REFIN 'd{1 if config['refin'] else 0}\n")
        f.write(f"`define CRC_REFOUT 'd{1 if config['refout'] else 0}\n")
        f.write(f"`define CRC_XOROUT 'h{config['xorout']:x}\n")
    
    return rtl_path

def generate_test_data(min_length, max_length):
    """生成随机测试数据"""
    length = random.randint(min_length, max_length)
    data = [random.randint(0, 255) for _ in range(length)]
    return data

def save_test_data(data, config_id, test_id, input_dir):
    """保存测试数据为16进制格式"""
    output_path = os.path.join(input_dir, f"test_data_c{config_id}_t{test_id}_input.dat")
    # 先写入数据长度，然后是16进制数据
    hex_data = ' '.join([f"{byte:02X}" for byte in data])
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"{len(data)}\n{hex_data}")
    return output_path

def main():
    args = parse_args()
    
    if args.seed is not None:
        random.seed(args.seed)
        print(f"使用随机种子: {args.seed}")
    
    # 获取脚本所在根目录
    script_dir = Path(__file__).parent.parent.parent.absolute()
    
    # 确保输出目录存在
    dirs = {
        "input": os.path.join(args.output_dir),
        "rtl_config": os.path.join(script_dir, "rtl_model", "settings")
    }
    
    print(f"配置文件将保存到: {dirs['rtl_config']}")
    
    for dir_path in dirs.values():
        os.makedirs(dir_path, exist_ok=True)
    
    # 记录生成的配置和测试数据
    configs = {}
    tests = []
    
    # 配置ID从1开始
    config_id = 1
    total_configs = 0
    
    # 生成四种类型的硬件配置
    config_types = ["standard", "mixed_one", "mixed_two", "reflect"]
    
    print(f"\n开始生成硬件RTL CRC测试数据...")
    
    for config_type in config_types:
        for i in range(args.n_configs):
            print(f"\n生成硬件CRC配置 #{config_id} (类型: {config_type})...")
            
            # 生成指定类型的硬件CRC配置
            config = generate_hardware_config(config_type)
            
            # 保存配置
            rtl_path = save_rtl_config(
                config, config_id,
                dirs["rtl_config"]
            )
            
            # 显示配置信息
            print(f"  多项式: CRC-{config['width']} = 0x{config['poly']:x}")
            print(f"  初始值: 0x{config['init']:x}")
            print(f"  结果异或值: 0x{config['xorout']:x}")
            print(f"  输入反转: {'是' if config['refin'] else '否'}")
            print(f"  输出反转: {'是' if config['refout'] else '否'}")
            
            # 记录配置信息
            configs[config_id] = {
                "width": config["width"],
                "poly": f"0x{config['poly']:x}",
                "type": "hardware",
                "reflection_type": config["type_name"],
                "rtl_config": os.path.basename(rtl_path)
            }
            
            # 为配置生成测试数据
            print(f"  生成测试数据...")
            for test_id in range(1, args.n_tests + 1):
                data = generate_test_data(args.min_length, args.max_length)
                data_path = save_test_data(data, config_id, test_id, dirs["input"])
                
                tests.append({
                    "config_id": config_id,
                    "config_type": "hardware",
                    "reflection_type": config["type_name"],
                    "test_id": test_id,
                    "length": len(data),
                    "file": os.path.basename(data_path)
                })
                
                print(f"    测试 #{test_id}: {len(data)} 字节 -> {os.path.basename(data_path)}")
            
            # 增加配置ID
            config_id += 1
            total_configs += 1
    
    # 保存摘要
    summary = {
        "configs": configs,
        "test_data": tests,
        "total_configs": total_configs,
        "total_tests": total_configs * args.n_tests,
        "config_types": config_types
    }
    
    summary_path = os.path.join(dirs["input"], "rtl_generation_summary.json")
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n生成完成! 总共生成了 {total_configs} 个RTL CRC配置")
    print(f"  标准配置: {args.n_configs} 个")
    print(f"  混合配置1 (refin=true,refout=false): {args.n_configs} 个")
    print(f"  混合配置2 (refin=false,refout=true): {args.n_configs} 个")
    print(f"  反转配置: {args.n_configs} 个")
    print(f"共生成了 {total_configs * args.n_tests} 个测试数据。")
    print(f"摘要已保存至: {summary_path}")
    print(f"配置文件保存在: {dirs['rtl_config']}")
    print(f"测试数据保存在: {dirs['input']}")

if __name__ == "__main__":
    main()