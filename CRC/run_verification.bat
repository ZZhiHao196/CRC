@echo off
REM CRC验证流程脚本
echo ==== CRC算法验证流程 ====

REM 确保输出目录存在
mkdir dataset\input 2>nul
mkdir dataset\rtl_data 2>nul
mkdir dataset\output 2>nul
mkdir settings\python_setting 2>nul
mkdir settings\rtl_setting 2>nul

REM 1. 生成测试数据和配置
echo.
echo [1/4] 生成CRC配置和测试数据...
cd python_model
python data_generator.py --n-configs 3 --n-tests 5 --min-length 3 --max-length 20 --seed 42
cd ..

REM 2. 验证Python CRC实现
echo.
echo [2/4] 验证Python CRC实现...
cd python_model
python verify_crc.py --verbose
cd ..

REM 3. 运行RTL仿真
echo.
echo [3/4] 运行RTL仿真...
echo 请手动运行RTL仿真，以生成RTL结果。
echo 确保RTL结果保存在 dataset\rtl_data 目录中。
REM 在这里可以添加适合你的RTL仿真命令，例如：
REM cd rtl_model
REM iverilog -o crc_sim crc.v crc_process_byte.v reverse_bits.v crc_tb.v
REM vvp crc_sim
REM cd ..

REM 4. 比较RTL和模型结果
echo.
echo [4/4] 比较RTL和Python模型结果...
cd python_model
python compare_model.py --verbose
cd ..

echo.
echo ==== 验证流程完成 ====
echo 详细报告：
echo   - Python模型验证报告：dataset\output\verification_report.txt
echo   - RTL与模型比较报告：dataset\output\rtl_comparison_report.txt
pause 