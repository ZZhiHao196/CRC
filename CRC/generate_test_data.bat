@echo off
echo 正在生成CRC测试数据...
python python_model/scr/crc_rtl_generator.py --n-configs 1 --n-tests 4 --min-length 5 --max-length 20
echo 测试数据生成完成 