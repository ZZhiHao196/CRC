@echo off
echo ==== CRC算法验证流程 ====

REM 保存当前目录
set CURRENT_DIR=%CD%

REM 确保输出目录存在
mkdir dataset\Test_Model\model_data 2>nul

REM 1. 生成测试数据
echo.
echo [1/4] 生成CRC测试数据...
cd %CURRENT_DIR%
call generate_test_data.bat

REM 2. 软件模型与标准库比较
echo.
echo [2/4] 验证软件模型正确性...
cd %CURRENT_DIR%
python python_model/scr/crc_model_validator.py --verbose

REM 3. 运行RTL仿真
echo.
echo [3/4] 运行RTL仿真...
cd %CURRENT_DIR%
call run_sim.bat

REM 返回到原来的目录
cd %CURRENT_DIR%

REM 4. 比较RTL和软件模型结果
echo.
echo [4/4] 比较RTL与软件模型结果...
cd %CURRENT_DIR%
python python_model/scr/crc_rtl_validator.py --verbose

echo.
echo ==== 验证流程完成 ====
echo 请查看比较结果
pause 