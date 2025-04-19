import os
import glob
import json
import crcmod
import argparse
from CRC import calculate_crc


def parse_args():
    parser = argparse.ArgumentParser(description='验证CRC计算结果')
    parser.add_argument('--config-dir', type=str, default='./python_model/settings', help='Python配置目录')
    parser.add_argument('--input-dir', type=str, default='./dataset/Test_Algorithm/input', help='输入数据目录')
    parser.add_argument('--output-dir', type=str, default='./dataset/Test_Algorithm/output', help='输出结果目录')
    parser.add_argument('--verbose', action='store_true', help='显示详细信息')
    return parser.parse_args()

def load_configs(config_dir):
    """加载所有CRC配置文件"""
    configs = []
    config_files = glob.glob(os.path.join(config_dir, 'crc_config_*.json'))
    
    for cfg_file in config_files:
        with open(cfg_file, 'r') as f:
            config = json.load(f)
            # 正确提取配置ID（匹配crc_config_1.json中的1）
            config_id = os.path.basename(cfg_file).split('_')[2].split('.')[0]
            config['id'] = config_id
            configs.append(config)
            print(f"加载配置: {config_id}:{config['width']}位CRC")
    return configs

def load_test_data(input_dir):
    """加载所有测试数据"""
    test_cases = []
    for data_file in glob.glob(os.path.join(input_dir, 'test_data_*.dat')):
        # 解析文件名格式: test_data_c1_t2.dat
        filename = os.path.basename(data_file)
        parts = filename[:-4].split('_')  # 移除.dat扩展名后分割
        
        # 确保格式正确且包含足够的部分
        if len(parts) >= 4 and parts[0] == "test" and parts[1] == "data":
            config_id = parts[2][1:]  # 提取c1中的1
            test_id = parts[3][1:]    # 提取t2中的2
        else:
            print(f"警告: 跳过无效文件名格式 {filename}")
            continue

        with open(data_file, 'r', encoding='utf-8') as f:
            # 假设文件包含用空格分隔的十六进制值
            hex_str = f.read().strip()
            # 解析十六进制值到整数列表
            data = [int(x, 16) for x in hex_str.split()]
            # 创建对应的bytes对象
            raw_bytes = bytes(data)
            
        test_cases.append({
            'config_id': config_id,
            'test_id': test_id,
            'data': data,          # 整数列表 [1, 2, 3]
            'raw_data': raw_bytes  # bytes对象 b'\x01\x02\x03'
        })
        print(f"已加载测试用例 {filename} (配置: {config_id}, 测试: {test_id}, {len(data)}字节)")
    return test_cases


def validate_crc(config, test_case):
    width = config['width']
    poly = config['poly']
    init = config['init']
    rev = config['rev']
    xorout = config['xorout']
    
    # 创建crcmod标准函数（使用字节数组输入）
    crc_func = crcmod.mkCrcFun(
        poly,
        initCrc=init,
        rev=rev,
        xorOut=xorout)
    
    # 使用相应数据格式调用函数
    #print(test_case['data'])
    #print(test_case['raw_data'])
    custom_crc = calculate_crc(test_case['data'], width, poly, init, rev, rev, xorout)
    official_crc = crc_func(test_case['raw_data'])
    
    # 生成十六进制字符串表示
    custom_hex = f"0x{custom_crc:X}"
    official_hex = f"0x{official_crc:X}"
    
    return {
        'config_id': test_case['config_id'],
        'test_id': test_case['test_id'],
        'custom': custom_crc,
        'official': official_crc,
        'custom_hex': custom_hex,         # 添加十六进制字符串表示
        'official_hex': official_hex,     # 添加十六进制字符串表示
        'match': custom_crc == official_crc
    }

def save_results(results, output_dir):
    """保存验证结果到文件"""
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存每个测试用例的结果
    for result in results:
        filename = f"result_c{result['config_id']}_t{result['test_id']}.dat"
        with open(os.path.join(output_dir, filename), 'w') as f:
            f.write(f"Custom CRC: 0x{result['custom']:X}\n")
            f.write(f"Official CRC: 0x{result['official']:X}\n")
            f.write(f"Match: {result['match']}\n")
    
    # 生成总结报告
    report_path = os.path.join(output_dir, 'summary_report.txt')
    total = len(results)
    matches = sum(1 for r in results if r['match'])
    
    with open(report_path, 'w') as f:
        f.write("CRC Validation Summary\n")
        f.write("======================\n")
        f.write(f"Total Tests: {total}\n")
        f.write(f"Matches: {matches}\n")
        f.write(f"Mismatches: {total - matches}\n")
        f.write(f"Success Rate: {matches/total*100:.2f}%\n")
        
        # 记录不匹配的用例
        if total - matches > 0:
            f.write("\nMismatch Details:\n")
            for res in filter(lambda x: not x['match'], results):
                f.write(f"Config {res['config_id']} Test {res['test_id']}:\n")
                f.write(f"  Custom: 0x{res['custom']:X}\n")
                f.write(f"  Official: 0x{res['official']:X}\n\n")

def main():
    args = parse_args()
    
    # 显示运行参数
    print("CRC验证工具启动")
    print(f"配置目录: {args.config_dir}")
    print(f"测试数据目录: {args.input_dir}")
    print(f"结果输出目录: {args.output_dir}")
    
    # 加载配置和测试数据
    configs = load_configs(args.config_dir)
    test_cases = load_test_data(args.input_dir)
    
    # 检查数据加载情况
    if not configs:
        print("错误: 未能加载任何配置文件，请检查配置目录")
        return
    
    if not test_cases:
        print("错误: 未能加载任何测试用例，请检查测试数据目录")
        return
    
    # 执行验证
    print("\n开始CRC验证...")
    results = []
    matched = 0
    mismatched = 0
    
    for config in configs:
        # 找到该配置对应的测试用例
        related_tests = [t for t in test_cases if t['config_id'] == config['id']]
        
        if not related_tests:
            print(f"  警告: 配置 #{config['id']} 没有对应的测试用例")
            continue
        
        print(f"\n验证配置 #{config['id']} ({len(related_tests)}个测试):")
        
        for test in related_tests:
            result = validate_crc(config, test)
            results.append(result)
            
            # 输出结果
            status = "匹配" if result['match'] else "不匹配"
            status_symbol = "✓" if result['match'] else "✗"
            
            print(f"  测试 #{test['test_id']}: {status_symbol} {status}")
            if args.verbose or not result['match']:
                print(f"    自定义: {result['custom_hex']}")
                print(f"    官方库: {result['official_hex']}")
            
            # 更新计数
            if result['match']:
                matched += 1
            else:
                mismatched += 1
    
    # 保存结果
    if results:
        report_file = save_results(results, args.output_dir)
    
    # 打印总结
    total = len(results)
    print("\n" + "="*50)
    print("CRC验证完成!")
    print(f"总测试数: {total}")
    print(f"匹配: {matched}")
    print(f"不匹配: {mismatched}")
    if total > 0:
        print(f"成功率: {matched/total*100:.2f}%")
    
    # 如果有不匹配的结果，特别显示
    if mismatched > 0:
        print("\n不匹配的测试:")
        for res in filter(lambda x: not x['match'], results):
            print(f"  配置 #{res['config_id']} 测试 #{res['test_id']}")
            print(f"    自定义: {res['custom_hex']}")
            print(f"    官方库: {res['official_hex']}")
    
    print("="*50)
    print(f"详细结果已保存到: {args.output_dir}")

if __name__ == "__main__":
    main()