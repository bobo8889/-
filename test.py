from controller.utils import hex2bin, bin2int, crc
from textwrap import wrap
from controller.utils import DICT_MAPPER


def main():
    # message = "80E1969458B542A5CB38B8E14373"
    # message = "8D780889585302F9694664009FC0"
    message = "8D4840D6202CC371C32CE0576098"
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
    # if df != 17:
    #     print("error: not Mode-S Transponder")
    #     return
    """
    传入报文到 crc 函数进行 CRC 校验
    若校验失败则报错
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
            result += str(DICT_MAPPER[v])
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
