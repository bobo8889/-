from typing import Tuple
from textwrap import wrap

DICT_MAP = {
    1: "A",
    2: "B",
    3: "C",
    4: "D",
    5: "E",
    6: "F",
    7: "G",
    8: "H",
    9: "I",
    10: "J",
    11: "K",
    12: "L",
    13: "M",
    14: "N",
    15: "O",
    16: "P",
    17: "Q",
    18: "R",
    19: "S",
    20: "T",
    21: "U",
    22: "V",
    23: "W",
    24: "X",
    25: "Y",
    26: "Z",
    32: "_",
    48: 0,
    49: 1,
    50: 2,
    51: 3,
    52: 4,
    53: 5,
    54: 6,
    55: 7,
    56: 8,
    57: 9,
}


def hex2bin(hexstr: str) -> str:
    """将十六进制字符串转换为二进制字符串

    Args:
        hexstr (str): 十六进制字符串

    Returns:
        str: 二进制字符串
    """
    num_of_bits = len(hexstr) * 4
    binstr = bin(int(hexstr, 16))[2:].zfill(int(num_of_bits))
    return binstr


def bin2int(binstr: str) -> int:
    """将二进制字符串转换为十进制整数

    Args:
        binstr (str): 二进制字符串

    Returns:
        int: 十进制整数
    """
    return int(binstr, 2)


def crc(msg: int) -> Tuple[int, bool]:
    """ADS-B 报文 CRC 校验

    Args:
        msg (str): ADS-B 完整报文

    Returns:
        Tuple[int, bool]: CRC 校验结果，校验是否失败
    """
    # CRC 生成多项式系数由 ADS-B 协议事先定义好
    G = [0b11111111, 0b11111010,
         0b00000100, 0b10000000]

    msgbin = hex2bin(msg)
    msgbin_split = wrap(msgbin, 8)
    mbytes = list(map(bin2int, msgbin_split))

    for ibyte in range(len(mbytes) - 3):
        for ibit in range(8):
            mask = 0x80 >> ibit
            bits = mbytes[ibyte] & mask
            if bits > 0:
                mbytes[ibyte] = mbytes[ibyte] ^ (G[0] >> ibit)
                mbytes[ibyte + 1] = mbytes[ibyte + 1] ^ (
                    0xFF & ((G[0] << 8 - ibit) | (G[1] >> ibit))
                )
                mbytes[ibyte + 2] = mbytes[ibyte + 2] ^ (
                    0xFF & ((G[1] << 8 - ibit) | (G[2] >> ibit))
                )
                mbytes[ibyte + 3] = mbytes[ibyte + 3] ^ (
                    0xFF & ((G[2] << 8 - ibit) | (G[3] >> ibit))
                )

    result = (mbytes[-3] << 16) | (mbytes[-2] << 8) | mbytes[-1]
    return result, result != 0


def main():
    message = "8D781CE6250C3071D71DA0AF97DB"
    # message = "8D780889585302F9694664009FC0"
    # message = "8D4840D6202CC371C32CE0576098"
    """
    判断长度是否合规
    讯息长度恒定为 112 bits，即 28 个十六进制数
    """
    if len(message) * 4 != 112:
        print("error: length not match")
        return
    """
    取得 Downlink Format，下称 DF
    取 message[:2] 高 5 位，即右移 3 位
    """
    df = (int(message[:2], 16) >> 3)
    print(f"Downlink Format: {df}")
    """
    若 DF 为 17，表示 Mode-S Transponder
    其他 Downlink Format 暂不处理
    """
    if df != 17:
        print("error: not Mode-S Transponder")
        return
    """
    取得 Parity Interrogator，下称 PI，位于 message[-6:]
    取得报文非 PI 区段，即 message[:22]
    传入函数进行 CRC 校验，若校验失败则报错
    """
    _, err = crc(message)
    if err:
        print("error: CRC failed")
        return
    """
    取得 Additional Identifier，下称 CA
    取 message[:2] 低 3 位，即按位与 0b111
    """
    ca = int(message[:2], 16) & 0b111
    print(f"Additional Identifier: {ca}")
    """
    取得 ICAO Address，此代码唯一标识飞机
    直接取讯息 message[2:8]，不需做其他转换
    """
    icao = message[2:8]
    print(f"ICAO Address: {icao}")
    """
    取得 Data，即 ADS-B 讯息正文
    取 message[8:22]，不需做其他转换
    """
    data = message[8:22]
    print(f"ADSB Data: {data}")
    """
    取得 Type Code，下称 TC
    Type Code 来自 DATA 首 5 比特
    即取 data[:2] 高 5 位，即右移 3 位
    """
    tc = int(data[:2], 16) >> 3
    print(f"Type Code: {tc}")
    """
    In case DF == 17 and TC >= 1 and TC <= 4 
        可以确认为飞机识别讯息
        航班号在讯息 data 中
    In case DF == 17 and TC >= 5 and TC <= 8
        可以确认为地面讯息
        讯息中包含地速和航向角
    In case DF == 17 and TC >= 9 and TC <= 18
        位置讯息包含高度
        气压高度以英尺为单位
    In case DF == 17 and TC == 19
        速度讯息
        适用于地速和空速
        通过子类型识别讯息类型
    In case DF == 17 and TC >= 20 and TC <= 22
        位置讯息包含高度
        高度来自 GNSS，以米为单位
    In case DF == 17 and TC >= 23 and TC <= 31
        保留位
        直接返回
    In other cases
        返回错误
    """
    if tc >= 1 and tc <= 4:
        # Now we have a callsign
        msgbin = hex2bin(data[2:])
        msgbin_split = wrap(msgbin, 6)
        mbytes = list(map(bin2int, msgbin_split))
        result = ""
        for _, v in enumerate(mbytes):
            result += str(DICT_MAP[v])
        print(f"Callsign: {result}")
    elif tc >= 5 and tc <= 8:
        # Now we have a ground speed & track angle
        pass
    elif tc >= 9 and tc <= 18:
        # Now we have a barometric altitude
        pass
    elif tc == 19:
        # Now we have a airborne velocity message
        pass
    elif tc >= 20 and tc <= 22:
        # Now we have a GNSS height
        pass
    else:
        print("error: unknown type code")
        return


if __name__ == '__main__':
    main()
