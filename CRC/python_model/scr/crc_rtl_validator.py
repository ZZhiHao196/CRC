#!/usr/bin/env python3
"""
CRC RTL与软件模型比较工具
比较RTL仿真结果与Python软件模型的计算结果是否一致
"""

import os
import json
import glob
import argparse
import importlib.util
from pathlib import Path
from CRC import calculate_crc
import sys

# 获取项目根目录（脚本的上上级目录）
ROOT_DIR = Path(__file__).parent.parent.parent.absolute()

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="CRC RTL与软件模型比较工具")
    parser.add_argument('--rtl-setting-dir', type=str, 
                      default=str(ROOT_DIR / 'rtl_model' / 'settings'), 
                      help="RTL CRC配置目录")
    parser.add_argument('--input-dir', type=str, 
                      default=str(ROOT_DIR / 'dataset' / 'Test_Model' / 'input'), 
                      help="测试数据输入目录")
    parser.add_argument('--rtl-output-dir', type=str, 
                      default=str(ROOT_DIR / 'dataset' / 'Test_Model' / 'rtl_data'), 
                      help="RTL仿真结果目录")
    parser.add_argument('--model-output-dir', type=str, 
                      default=str(ROOT_DIR / 'dataset' / 'Test_Model' / 'model_data'), 
                      help="软件模型结果输出目录")
    parser.add_argument('--verbose', action='store_true', 
                        help="显示详细信息")
    return parser.parse_args()

def load_rtl_config(config_file):
    """从RTL配置文件加载CRC参数"""
    config = {}
    try:
        print(f"读取配置文件: {config_file}")
        with open(config_file, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            # 跳过注释和空行
            if not line or line.startswith('//'):
                continue
                
            if '`define' in line:
                # 将行按空格分割
                parts = line.split()
                if len(parts) < 3:
                    continue
                    
                # 提取关键部分：名称和值
                define_keyword = parts[0]  # 应该是 `define
                param_name = parts[1]      # 例如 `CRC_WIDTH
                param_value = parts[2]     # 例如 'd16 或 'h10c21
                
                # 移除名称中的反引号
                param_name = param_name.replace('`', '')
                
                # 处理Verilog数值格式
                if "'" in param_value:
                    # 检查'd或'h格式
                    if param_value.startswith("'d"):
                        # 十进制值
                        actual_value = int(param_value[2:], 10)
                    elif param_value.startswith("'h"):
                        # 十六进制值
                        actual_value = int(param_value[2:], 16)
                    else:
                        # 其他格式，保持原样
                        actual_value = param_value
                else:
                    # 没有特殊格式，尝试直接转换
                    try:
                        actual_value = int(param_value)
                    except ValueError:
                        actual_value = param_value
                
                # 保存到配置
                if param_name == "CRC_WIDTH":
                    config['width'] = actual_value
                elif param_name == "CRC_POLY":
                    config['poly'] = hex(actual_value) if isinstance(actual_value, int) else actual_value
                elif param_name == "CRC_INIT":
                    config['init'] = hex(actual_value) if isinstance(actual_value, int) else actual_value
                elif param_name == "CRC_REFIN":
                    config['refin'] = actual_value == 1 if isinstance(actual_value, int) else (actual_value == '1')
                elif param_name == "CRC_REFOUT":
                    config['refout'] = actual_value == 1 if isinstance(actual_value, int) else (actual_value == '1')
                elif param_name == "CRC_XOROUT":
                    config['xorout'] = hex(actual_value) if isinstance(actual_value, int) else actual_value
                
                print(f"  解析参数: {param_name} = {param_value} -> {config.get(param_name.lower().replace('crc_', ''))}")
        
        # 检查是否获取了所有必要参数
        required_params = ['width', 'poly', 'init', 'refin', 'refout', 'xorout']
        missing_params = [p for p in required_params if p not in config]
        
        if missing_params:
            print(f"  警告: 缺少必要参数: {', '.join(missing_params)}")
            return None
            
        print(f"  成功加载配置: {config}")
        return config
        
    except Exception as e:
        print(f"错误：读取配置文件失败 {config_file}: {e}")
        import traceback
        traceback.print_exc()
        return None

def load_test_data(input_file):
    """从测试数据文件加载数据"""
    try:
        with open(input_file, 'r') as f:
            lines = f.readlines()
            
        if len(lines) < 2:
            print(f"错误：测试数据文件格式不正确 {input_file}")
            return None
            
        # 第一行是数据长度
        data_length = int(lines[0].strip())
        
        # 第二行是十六进制数据
        hex_values = lines[1].strip().split()
        
        # 转换为整数列表
        data = [int(hex_val, 16) for hex_val in hex_values]
        
        if len(data) != data_length:
            print(f"警告：数据长度({len(data)})与声明长度({data_length})不一致 - {input_file}")
            
        return data
    except Exception as e:
        print(f"错误：读取测试数据失败 {input_file}: {e}")
        return None

def load_rtl_results(rtl_output_dir):
    """加载RTL仿真结果"""
    rtl_results = {}
    
    # 查找所有RTL输出文件
    output_files = glob.glob(os.path.join(rtl_output_dir, '*.dat'))
    
    for file_path in output_files:
        try:
            # 从文件名中提取配置ID和测试ID
            filename = os.path.basename(file_path)
            if '_output.dat' not in filename:
                continue
                
            # 解析文件名，例如 test_data_c1_t1_output.dat
            parts = filename.replace('_output.dat', '').split('_')
            if len(parts) < 4:
                print(f"警告：无法解析RTL输出文件名：{filename}")
                continue
                
            config_id = parts[2]
            test_id = parts[3]
            
            # 读取CRC结果
            with open(file_path, 'r') as f:
                crc_hex = f.read().strip()
                crc_value = int(crc_hex, 16)
                
            # 保存结果
            key = (config_id, test_id)
            rtl_results[key] = crc_value
            
        except Exception as e:
            print(f"错误：处理RTL结果文件时出错 {file_path}: {e}")
    
    return rtl_results

def run_software_model(input_dir, configs, model_output_dir):
    """运行软件模型并保存结果"""
    os.makedirs(model_output_dir, exist_ok=True)
    model_results = {}
    
    # 遍历所有输入文件
    input_files = glob.glob(os.path.join(input_dir, '*_input.dat'))
    
    for input_file in input_files:
        try:
            # 解析文件名
            filename = os.path.basename(input_file)
            parts = filename.replace('_input.dat', '').split('_')
            
            if len(parts) < 4:
                print(f"警告：无法解析输入文件名：{filename}")
                continue
                
            # 正确提取配置ID - 从"c1"中提取"1"
            config_id = parts[2].replace('c', '')
            test_id = parts[3]
            
            # 检查是否有对应的配置
            config_file = f"crc_config_{config_id}.vh"
            if config_file not in configs:
                print(f"警告：无法找到配置 {config_file} 对应的输入 {filename}")
                continue
                
            config = configs[config_file]
            
            # 加载测试数据
            data = load_test_data(input_file)
            if data is None:
                continue
                
            # 计算CRC
            width = config['width']
            poly = int(config['poly'], 16)
            init = int(config['init'], 16)
            refin = config['refin']
            refout = config['refout']
            xorout = int(config['xorout'], 16)
            
            crc_value = calculate_crc(data, width, poly, init, refin, refout, xorout)
            
            # 保存到模型结果
            key = (parts[2], test_id)  # 保留原始配置ID格式(c1)用于匹配
            model_results[key] = crc_value
            
            # 保存结果到输出文件
            output_filename = filename.replace('_input.dat', '_output.dat')
            output_path = os.path.join(model_output_dir, output_filename)
            
            with open(output_path, 'w') as f:
                # 输出十六进制结果
                f.write(f"{crc_value:x}")
                
            if args.verbose:
                print(f"计算完成: {filename} -> CRC = 0x{crc_value:x}")
                
        except Exception as e:
            print(f"错误：处理输入文件时出错 {input_file}: {e}")
    
    return model_results

def compare_results(model_results, rtl_results, verbose=False):
    """比较模型结果和RTL结果"""
    # 比较结果
    comparison = []
    
    # 获取所有唯一的测试
    all_keys = set(model_results.keys()) | set(rtl_results.keys())
    
    for key in sorted(all_keys):
        config_id, test_id = key
        
        model_crc = model_results.get(key)
        rtl_crc = rtl_results.get(key)
        
        if model_crc is not None and rtl_crc is not None:
            # 两者都有结果
            match = model_crc == rtl_crc
            status = "匹配" if match else "不匹配"
        else:
            # 缺少结果
            match = False
            status = "缺少结果"
        
        comparison.append({
            'config_id': config_id,
            'test_id': test_id,
            'model_crc': model_crc,
            'rtl_crc': rtl_crc,
            'match': match,
            'status': status
        })
        
        if verbose:
            print(f"测试 c{config_id}_t{test_id}: {status}")
            if model_crc is not None:
                print(f"  模型CRC: 0x{model_crc:x}")
            else:
                print("  模型CRC: 缺少")
                
            if rtl_crc is not None:
                print(f"  RTL CRC: 0x{rtl_crc:x}")
            else:
                print("  RTL CRC: 缺少")
            print()
    
    return comparison

def main():
    global args
    # 解析命令行参数
    args = parse_arguments()
    
    # 加载RTL配置
    configs = {}
    config_files = glob.glob(os.path.join(args.rtl_setting_dir, '*.vh'))
    for config_file in config_files:
        config = load_rtl_config(config_file)
        if config:
            filename = os.path.basename(config_file)
            configs[filename] = config
    
    if not configs:
        print("错误：未找到有效的RTL CRC配置")
        return
    
    print(f"加载了 {len(configs)} 个RTL配置")
    
    # 检查RTL结果目录中的文件模式，确定当前激活的配置
    rtl_files = glob.glob(os.path.join(args.rtl_output_dir, '*.dat'))
    active_config = None
    
    # 检测是哪个配置被启用了
    for file_path in rtl_files:
        filename = os.path.basename(file_path)
        # 分析文件名确定配置ID
        if '_c1_' in filename:
            active_config = '1'
            print("检测到启用的是标准模式 (Crc_Standard)")
            break
        elif '_c2_' in filename:
            active_config = '2'
            print("检测到启用的是混合模式一 (Crc_Mixed1)")
            break
        elif '_c3_' in filename:
            active_config = '3'
            print("检测到启用的是混合模式二 (Crc_Mixed2)")
            break
        elif '_c4_' in filename:
            active_config = '4'
            print("检测到启用的是反转模式 (Crc_Reverse)")
            break
    
    if active_config is None:
        print("警告：无法确定当前激活的CRC配置，将测试所有配置")
    else:
        print(f"只处理配置 {active_config} 的测试数据")
    
    # 运行软件模型
    print("运行软件模型计算CRC...")
    filtered_configs = configs
    
    # 如果确定了激活的配置，只处理该配置
    if active_config:
        config_file = f"crc_config_{active_config}.vh"
        if config_file in configs:
            filtered_configs = {config_file: configs[config_file]}
        else:
            print(f"警告：找不到配置文件 {config_file}，将使用所有可用配置")
    
    # 使用筛选后的配置运行软件模型
    model_results = run_software_model(args.input_dir, filtered_configs, args.model_output_dir)
    
    # 加载RTL结果
    print("加载RTL仿真结果...")
    rtl_results = load_rtl_results(args.rtl_output_dir)
    
    # 比较结果
    print("比较结果...")
    comparison = compare_results(model_results, rtl_results, args.verbose)
    
    # 打印总结
    total = len(comparison)
    matches = sum(1 for r in comparison if r['match'])
    mismatches = sum(1 for r in comparison if not r['match'] and r['status'] == "不匹配")
    missing = sum(1 for r in comparison if r['status'] == "缺少结果")
    
    print(f"\nCRC RTL与软件模型比较完成:")
    print(f"  总测试数: {total}")
    print(f"  匹配: {matches}")
    print(f"  不匹配: {mismatches}")
    print(f"  缺少结果: {missing}")
    
    if total > 0:
        print(f"  成功率: {matches/total*100:.2f}%")
    
    # 输出不匹配的测试详情
    if mismatches > 0:
        print("\n不匹配的测试:")
        for result in comparison:
            if not result['match'] and result['status'] == "不匹配":
                config_id = result['config_id']
                test_id = result['test_id']
                model_crc = result['model_crc']
                rtl_crc = result['rtl_crc']
                
                print(f"  配置: c{config_id}_t{test_id}")
                print(f"  模型CRC: 0x{model_crc:x}")
                print(f"  RTL CRC: 0x{rtl_crc:x}")
                print()

if __name__ == "__main__":
    main() 