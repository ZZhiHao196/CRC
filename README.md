# CRC 验证框架

这个项目包含了 CRC（循环冗余校验）算法的软件实现和 RTL 硬件实现，以及一个完整的验证框架，用于确保两种实现的一致性。

## 项目结构

- `python_model/` - CRC 软件实现
  - `scr/` - 源代码
    - `CRC.py` - CRC 基本实现
    - `crc_rtl_generator.py` - 生成 RTL 配置和测试数据
    - `crc_rtl_validator.py` - 验证 RTL 实现与软件模型的一致性
    - `crc_model_validator.py` - 验证软件模型与标准库的一致性
  - `settings/` - CRC 配置文件
- `rtl_model/` - CRC 硬件实现

  - `src/` - RTL 源代码
    - `crc.v` - CRC 顶层模块
    - `crc_process_byte.v` - CRC 字节处理模块
  - `settings/` - RTL 配置文件（.vh 头文件）
  - `sim/` - 仿真相关文件
    - `crc_tb.v` - CRC 测试平台

- `dataset/` - 测试数据和结果
  - `Test_Model/` - 模型测试数据
    - `input/` - 测试输入数据
    - `rtl_data/` - RTL 实现结果
    - `model_data/` - 软件模型结果
  - `Test_Algorithm/` - 算法测试数据
- `.vscode/` - VSCode/Cursor IDE 配置
  - `tasks.json` - 预定义任务配置，用于编译、仿真和波形查看

## 批处理文件

- `generate_test_data.bat` - 生成 CRC 测试数据
- `run_sim.bat` - 运行 RTL 仿真
- `run_validation.bat` - 运行完整验证流程

## CRC 实现

本项目支持以下四种 CRC 模式：

1. **标准模式 (Standard)** - 无位反转，输入和输出保持原始位序
2. **混合模式一 (Mixed One)** - 输入位反转，输出不反转
3. **混合模式二 (Mixed Two)** - 输入不反转，输出位反转
4. **反转模式 (Reflect)** - 输入和输出都进行位反转

CRC 计算支持可配置的参数：

- 位宽 (Width) - CRC 位数
- 多项式 (Polynomial)
- 初始值 (Initial Value)
- 输入反转 (RefIn)
- 输出反转 (RefOut)
- 输出异或值 (XorOut)

## 验证流程

完整的验证流程包含四个步骤：

1. **生成测试数据** - 生成各种 CRC 配置和测试用例
2. **验证软件模型** - 将软件实现与标准库对比，确保软件算法正确
3. **RTL 仿真** - 运行硬件模型仿真
4. **比较 RTL 与软件** - 确保软件和硬件实现结果一致

## 使用方法

### 生成测试数据

```
generate_test_data.bat
```

这将生成 CRC 配置文件和测试数据。配置文件保存在`rtl_model/settings/`目录，测试数据保存在`dataset/Test_Model/input/`目录。

### 验证软件模型

```
python python_model/scr/crc_model_validator.py --verbose
```

这将比较自己实现的 CRC 代码与官方库(如 crcmod)的结果，确保软件实现正确。

### 运行 RTL 仿真

```
run_sim.bat
```

这将使用 Icarus Verilog 编译并运行 RTL 仿真。仿真结果保存在`dataset/Test_Model/rtl_data/`目录。

### 运行软件模型并比较结果

```
python python_model/scr/crc_rtl_validator.py --verbose
```

这将运行软件模型并比较软件模型与 RTL 仿真的结果。

### 一键完成验证

```
run_validation.bat
```

这将依次执行所有步骤：生成测试数据，验证软件模型，运行 RTL 仿真，比较 RTL 与软件结果。

## RTL 仿真详解

本项目支持使用 Icarus Verilog 进行 RTL 级仿真，并使用 GTKWave 查看波形。

### 使用 VSCode/Cursor 任务运行仿真

项目包含预配置的任务，方便在 IDE 中快速执行仿真操作：

1. 打开命令面板（Ctrl+Shift+P 或 Cmd+Shift+P）
2. 输入"Tasks: Run Task"并选择
3. 选择以下任务之一：
   - **编译 Verilog** - 仅编译 RTL 代码
   - **运行仿真** - 编译并运行仿真
   - **查看波形** - 打开 GTKWave 查看生成的波形文件
   - **一键仿真** - 编译并运行仿真
   - **一键仿真并查看波形** - 完整流程，包括编译、运行和波形查看

### 手动运行仿真

也可以使用命令行手动运行仿真：

1. **编译 RTL 代码**

   ```bash
   cd rtl_model/sim
   iverilog -I../settings -I../src -o crc_sim.out crc_tb.v
   ```

2. **运行仿真**

   ```bash
   vvp crc_sim.out
   ```

3. **查看波形**
   ```bash
   gtkwave crc_test.vcd
   ```

### 波形分析

仿真生成的波形文件（crc_test.vcd）可以通过 GTKWave 打开。主要观察点包括：

- **clk** - 时钟信号
- **rst_n** - 复位信号
- **data_in** - 输入数据
- **data_valid** - 数据有效信号
- **start** - 开始新计算信号
- **crc_out** - CRC 计算结果
- **crc_ready** - 结果有效信号

### 仿真配置切换

仿真默认使用标准模式配置(Crc_Standard)。若要切换到其他模式：

1. 编辑`rtl_model/sim/crc_tb.v`文件
2. 修改顶部的宏定义，注释当前使用的模式，取消注释想要使用的模式：
   ```verilog
   // CRC配置选择
   `define Crc_Standard 1
   // `define Crc_Mixed1 1
   // `define Crc_Mixed2 1
   // `define Crc_Reverse 1
   ```

## 依赖项

- Python 3.6+
- crcmod 库 (用于软件模型验证)
- Icarus Verilog (用于 RTL 仿真)
- GTKWave (用于查看波形)

### 安装依赖

#### Windows

```bash
# 安装Python依赖
pip install crcmod

# 使用MSYS2安装Icarus Verilog和GTKWave
pacman -S mingw-w64-x86_64-iverilog
pacman -S mingw-w64-x86_64-gtkwave
```

#### Linux

```bash
# 安装Python依赖
pip install crcmod

# 安装Icarus Verilog和GTKWave
sudo apt-get install iverilog gtkwave  # Debian/Ubuntu
# 或
sudo yum install iverilog gtkwave      # CentOS/RHEL
```

## 开发者信息

本项目为 CRC 校验算法的验证框架，包含软件和硬件实现，可用于教学、研究和实际应用场景中的 CRC 实现验证。
