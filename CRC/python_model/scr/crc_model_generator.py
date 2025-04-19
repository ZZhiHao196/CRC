"""
软件算法CRC配置和测试数据生成器
"""
import os
import random
import argparse
import json
from pathlib import Path

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='生成软件CRC配置和测试数据')
    parser.add_argument('--n-configs', type=int, default=4, help='软件配置数量')
    parser.add_argument('--n-tests', type=int, default=5, help='每个配置要生成的测试数量')
    parser.add_argument('--min-length', type=int, default=3, help='测试数据最小长度(字节)')
    parser.add_argument('--max-length', type=int, default=100, help='测试数据最大长度(字节)')
    parser.add_argument('--seed', type=int, default=None, help='随机数种子(可选)')
    parser.add_argument('--output-dir', type=str, default='./dataset/Test_Algorithm', 
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

def generate_software_config():
    """生成软件测试用的CRC配置（使用单个rev参数）"""
    common_widths = [8, 16, 32]
    width = random.choice(common_widths)
    
    polynomial = generate_polynomial(width)
    
    config = {
        "width": width,
        "poly": polynomial,
        "init": (1 << width) - 1,  # 全1初始值
        "xorout": 0,               # 常用的0异或值
        "rev": random.choice([True, False])
    }
    
    return config

def save_json_config(config, config_id, python_dir):
    """保存软件配置为JSON格式"""
    python_config = {
        "width": config["width"],    # 宽度保持十进制
        "poly": config['poly'],      # 多项式
        "init": config['init'],      # 初始值
        "rev": config["rev"],        # 布尔值保持不变
        "xorout": config['xorout']   # 异或值
    }
    
    # 保存Python配置
    python_path = os.path.join(python_dir, f"crc_config_{config_id}.json")
    with open(python_path, 'w') as f:
        json.dump(python_config, f, indent=2, ensure_ascii=False)
    return python_path

def generate_test_data(min_length, max_length):
    """生成随机测试数据"""
    length = random.randint(min_length, max_length)
    data = [random.randint(0, 255) for _ in range(length)]
    return data

def save_test_data(data, config_id, test_id, input_dir):
    """保存测试数据为16进制格式"""
    output_path = os.path.join(input_dir, f"test_data_c{config_id}_t{test_id}.dat")
    # 将整数数组转换为16进制字符串并保存
    hex_data = ' '.join([f"{byte:02X}" for byte in data])
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(hex_data)
    return output_path

def main():
    args = parse_args()
    
    if args.seed is not None:
        random.seed(args.seed)
        print(f"使用随机种子: {args.seed}")
    
    # 确保输出目录存在
    dirs = {
        "input": os.path.join(args.output_dir, "input"),
        "python_config": "./python_model/settings"
    }
    
    for dir_path in dirs.values():
        os.makedirs(dir_path, exist_ok=True)
    
    # 记录生成的配置和测试数据
    configs = {}
    tests = []
    
    # 配置ID从1开始
    config_id = 1
    
    # 生成软件配置
    print(f"\n开始生成软件CRC测试数据...")
    for _ in range(args.n_configs):
        print(f"\n生成软件CRC配置 #{config_id}...")
        
        # 生成软件CRC配置
        config = generate_software_config()
        
        # 保存配置
        python_path = save_json_config(
            config, config_id,
            dirs["python_config"]
        )
        
        # 显示配置信息
        print(f"  多项式: CRC-{config['width']} = 0x{config['poly']:x}")
        print(f"  初始值: 0x{config['init']:x}")
        print(f"  结果异或值: 0x{config['xorout']:x}")
        print(f"  反转: {'是' if config['rev'] else '否'}")
        
        # 记录配置信息
        configs[config_id] = {
            "width": config["width"],
            "poly": f"0x{config['poly']:x}",
            "type": "software",
            "python_config": os.path.basename(python_path)
        }
        
        # 为配置生成测试数据
        print(f"  生成测试数据...")
        for test_id in range(1, args.n_tests + 1):
            data = generate_test_data(args.min_length, args.max_length)
            data_path = save_test_data(data, config_id, test_id, dirs["input"])
            
            tests.append({
                "config_id": config_id,
                "config_type": "software",
                "test_id": test_id,
                "length": len(data),
                "file": os.path.basename(data_path)
            })
            
            print(f"    测试 #{test_id}: {len(data)} 字节 -> {os.path.basename(data_path)}")
        
        # 增加配置ID
        config_id += 1
    
    # 保存摘要
    summary = {
        "configs": configs,
        "test_data": tests,
        "total_configs": args.n_configs,
        "total_tests": args.n_configs * args.n_tests
    }
    
    summary_path = os.path.join(dirs["input"], "generation_summary.json")
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n生成完成! 总共生成了 {args.n_configs} 个软件CRC配置。")
    print(f"共生成了 {args.n_configs * args.n_tests} 个测试数据。")
    print(f"摘要已保存至: {summary_path}")
    print(f"配置文件保存在: {dirs['python_config']}")
    print(f"测试数据保存在: {dirs['input']}")

if __name__ == "__main__":
    main()