import random
import crcmod

crc_table = []

def reverse_bits(value, bits):
    reversed_bits = 0
    for i in range(bits):
        if value & (1 << i):
            reversed_bits |= (1 << (bits - 1 - i))
    return reversed_bits

def create_clc_table(Width, poly, refin):
    mask = (1 << Width) - 1
    poly = poly & mask
    # Reverse the polynomial once if refin is True
    if refin:
        poly = reverse_bits(poly, Width)
    for byte in range(256):
        crc_byte = byte
        if refin:
            # Reflect input byte and process
            remain = reverse_bits(crc_byte, 8)
            for _ in range(8):
                if remain & 1:
                    remain = (remain >> 1) ^ poly
                else:
                    remain >>= 1
                remain &= mask
        else:
            # MSB-first processing
            remain = crc_byte << (Width - 8)
            for _ in range(8):
                if remain & (1 << (Width - 1)):
                    remain = (remain << 1) ^ poly
                else:
                    remain <<= 1
                remain &= mask
        crc_table.append(remain)

def crc_calculate(data_bytes, width, init, xor_out, refin, refout):
    mask = (1 << width) - 1
    crc = init & mask

    for byte in data_bytes:
        if refin:
            reversed_byte = reverse_bits(byte, 8)
            index = (crc ^ reversed_byte) & 0xFF
            crc = (crc >> 8) ^ crc_table[index]
        else:
            index = ((crc >> (width - 8)) ^ byte) & 0xFF
            crc = ((crc << 8) & mask) ^ crc_table[index]

    if refout:
        crc = reverse_bits(crc, width)
    crc ^= xor_out  
    crc &= mask
    return crc


def run_monitor_tests(num_tests=100, max_length=100):
   
    """
    :param num_tests: 随机测试的次数
    :param max_length: 随机生成数据的最大长度（字节数）
    """
    # 根据参数创建查找表（注意：全局变量 crc_table 会被填充）
    create_clc_table(16, 0x1021, refin=False)

    # 利用 crcmod 生成一个参考的 CRC-CCITT 计算函数
    # 注意：crcmod 的多项式需要加上最高位，即0x11021对应CRC-CCITT (XModem) 标准，
    #       且初始值、是否反转和异或输出需与原算法保持一致。
    crc16_func = crcmod.mkCrcFun(0x11021, initCrc=0xFFFF, rev=False, xorOut=0x0000)
    
    # 进行多次随机测试
    for i in range(num_tests):
        length = random.randint(1, max_length)
        # 随机生成一个 0~255 的字节列表
        data = [random.randint(0, 255) for _ in range(length)]
        # 计算我们实现的CRC值
        my_crc = crc_calculate(data, width=16, init=0xFFFF, xor_out=0x0000, refin=False, refout=False)
        # 计算参考库的CRC值
        expected_crc = crc16_func(bytes(data))
        if my_crc != expected_crc:
            print(f"Test {i+1} FAILED:")
            print(f"  Data:        {data}")
            print(f"  My CRC:      0x{my_crc:04X}")
            print(f"  Expected CRC:0x{expected_crc:04X}")
        else:
            print(f"Test {i+1} passed.")


