import math
from socket import socket
from typing import Tuple
from textwrap import wrap


def socket_find(sock: socket, signature: bytes, retry: int = 1) -> Tuple[bytes, bool]:
    """从 socket 中读取数据，直到读取到指定的数据

    Args:
        sock (socket): 创建好的 socket 实例
        signature (bytes): 指定的数据
        retry (int): 重试次数

    Returns:
        Tuple[bytes, bool]: 读取到的数据，读取是否失败
    """
    for _ in range(retry):
        data = sock.recv(len(signature))
        if data.startswith(signature):
            return data, False

    return b"", True


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


def floor(x: float) -> int:
    """向下取整

    Args:
        x (float): 浮点数

    Returns:
        int: 向下取整后的整数
    """
    return int(floor(x))


def msg_crc(msg: int) -> Tuple[int, bool]:
    """ADS-B 报文 CRC 校验

    Args:
        msg (str): ADS-B 完整报文

    Returns:
        Tuple[int, bool]: CRC 校验结果，校验是否失败
    """
    G = [
        0b11111111, 0b11111010,
        0b00000100, 0b10000000,
    ]
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


class ADSBDecoder:
    """ADS-B 报文解码器

    从 ADS-B 报文中解析出各种资讯

    Attributes:
        msg (str): 原始报文
    """

    msg: str

    def set_msg(self, msg: str) -> bool:
        """设定原始报文

        Args:
            msg (str): 原始报文内容

        Returns:
            bool: 报文长度是否不正确
        """
        if len(msg) != 28:
            return True
        self.msg = msg
        return False

    def get_icao(self) -> Tuple[str, bool]:
        """取得 ICAO 数据
        
        取得 ICAO 数据，若解码失败，返回的 ICAO 数据为问号

        Returns:
            Tuple[str, bool]: ICAO 数据，是否解码失败
        """
        if len(self.msg) == 0:
            return "?", True
        return self.msg[2:8], False

    def get_cpr_pos(self) -> Tuple[float, float, bool]:
        """取得 CPR 编码经纬度
        
        取得 CPR 编码经纬度，单位为度
        若解码失败，返回的经纬度均为 -1

        Returns:
            Tuple[float, float, bool]: CPR 编码纬度，CPR 编码经度，是否解码失败
        """
        if len(self.msg) != 28 or self.get_typecode() < 5 or self.get_typecode() > 18:
            return -1, -1, True
        msgbin = hex2bin(self.msg)
        cpr_lat = bin2int(msgbin[54:71]) / 131072.0
        cpr_lon = bin2int(msgbin[71:88]) / 131072.0
        return cpr_lat, cpr_lon, False

    def get_altitude(self) -> Tuple[int, bool]:
        """取得海拔高度
        
        海拔高度单位为英尺
        若解码失败，返回的海拔高度为 -1

        Returns:
            Tuple[int, bool]: 海拔高度，是否解码失败
        """
        if len(self.msg) != 28 or self.get_typecode() < 9 or self.get_typecode() > 18:
            return -1, True
        msgbin = hex2bin(self.msg)
        if msgbin[47]:
            n = bin2int(msgbin[40:47] + msgbin[48:52])
            alt = n * 25 - 1000
            return alt, False
        return 0, True

    def get_typecode(self) -> int:
        """取得 Type Code
        
        取得 Type Code，若解码失败，返回的 Type Code 为 -1

        Returns:
            int: Type Code
        """
        if len(self.msg) != 28:
            return -1
        msgbin = hex2bin(self.msg)
        return bin2int(msgbin[32:37])

    def get_callsign(self) -> Tuple[str, bool]:
        """取得航班号

        尝试从报文读取航班号
        若解码失败，返回的航班号为问号

        Returns:
            Tuple[str, bool]: 航班号，是否解码失败
        """
        if len(self.msg) != 28 or self.get_typecode() < 1 or self.get_typecode() > 4:
            return "?", True
        chars = '#ABCDEFGHIJKLMNOPQRSTUVWXYZ#####_###############0123456789######'
        msgbin = hex2bin(self.msg)
        csbin = msgbin[40:96]
        cs = chars[bin2int(csbin[0:6])]
        cs += chars[bin2int(csbin[6:12])]
        cs += chars[bin2int(csbin[12:18])]
        cs += chars[bin2int(csbin[18:24])]
        cs += chars[bin2int(csbin[24:30])]
        cs += chars[bin2int(csbin[30:36])]
        cs += chars[bin2int(csbin[36:42])]
        cs += chars[bin2int(csbin[42:48])]
        cs = cs.replace('#', '')
        return cs, False

    def get_oe_flag(self) -> int:
        msgbin = hex2bin(self.msg)
        return int(msgbin[53])

    def get_velocity(self) -> Tuple[int, float, int, str, bool]:
        if self.get_typecode() != 19:
            raise RuntimeError(
                "%s: Not a airborne velocity message" % self.msg)
        msgbin = hex2bin(self.msg)
        subtype = bin2int(msgbin[37:40])
        if subtype in (1, 2):
            v_ew_sign = bin2int(msgbin[45])
            v_ew = bin2int(msgbin[46:56]) - 1  # east-west velocity
            v_ns_sign = bin2int(msgbin[56])
            v_ns = bin2int(msgbin[57:67]) - 1  # north-south velocity
            v_we = -1 * v_ew if v_ew_sign else v_ew
            v_sn = -1 * v_ns if v_ns_sign else v_ns
            spd = math.sqrt(v_sn * v_sn + v_we * v_we)  # unit in kts
            hdg = math.atan2(v_we, v_sn)
            hdg = math.degrees(hdg)  # convert to degrees
            hdg = hdg if hdg >= 0 else hdg + 360  # no negative val
            tag = 'GS'
        else:
            hdg = bin2int(msgbin[46:56]) / 1024.0 * 360.0
            spd = bin2int(msgbin[57:67])
            tag = 'AS'
        vr_sign = bin2int(msgbin[68])
        vr = bin2int(msgbin[68:77])  # vertical rate
        rocd = -1 * vr if vr_sign else vr  # rate of climb/descend
        return int(spd), round(hdg, 1), int(rocd), tag, False
