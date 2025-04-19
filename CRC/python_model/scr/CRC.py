def reverse_bits(x, num_bits):
    """反转指定位数的位序"""
    reversed_x = 0
    for i in range(num_bits):
        reversed_x |= ((x >> i) & 1) << (num_bits - 1 - i)
    return reversed_x


def crc_process_byte(crc, byte, poly, width, refin):
    """处理单个字节的CRC计算"""
    # 1. 如果需要反转输入
    if refin:
        byte = reverse_bits(byte, 8)
    
    # 2. 直接将字节与CRC高位进行异或（避免一位一位处理）
    crc ^= (byte << (width - 8))
    
    # 3. 处理8个位
    for _ in range(8):
        # 判断最高位，使用位移判断避免额外计算
        if crc & (1 << (width - 1)):
            # 左移+异或多项式
            crc = ((crc << 1) ^ poly) & ((1 << width) - 1)
        else:
            # 仅左移
            crc = (crc << 1) & ((1 << width) - 1)
    
    return crc

def calculate_crc(data_bytes, width, poly, init, refin, refout, xorout):
    """计算字节序列的CRC校验值"""
    # 确保poly不包含最高位(如果已经包含)
    poly = poly & ((1 << width) - 1)
    
    crc = init
    for byte in data_bytes:
        crc = crc_process_byte(crc, byte, poly, width, refin)
    if refout:
        crc = reverse_bits(crc, width)
    crc ^= xorout
    crc &= (1 << width) - 1  # 确保结果在低width位
    return crc

# 示例用法
if __name__ == "__main__":
    # 示例参数（以CRC-8为例）
    width = 8
    poly = 0x07  # 多项式 x^8 + x^2 + x + 1 (隐式最高位)
    init = 0xff
    refin = True
    refout = False
    xorout = 0x00

    # 输入数据（假设输入S018F0转换为字节数组）
    input_data = [0x1,0x2,0x3,0x4,0x5,0x6,0x7,0x8,0x9]
    crc_result = calculate_crc(input_data, width, poly, init, refin, refout, xorout)
    print(f"CRC结果: 0x{crc_result:02X}")