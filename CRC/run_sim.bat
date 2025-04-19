@echo off
cd rtl_model

echo 准备配置文件...
rem 复制配置文件到sim目录


echo 编译CRC代码...
cd sim
iverilog -I../settings -I../src -o crc_sim.out crc_tb.v

if %ERRORLEVEL% EQU 0 (
  echo 编译成功，开始模拟...
  vvp crc_sim.out
) else (
  echo 编译失败，请检查错误信息
)
