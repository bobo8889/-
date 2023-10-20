from socket import socket
from typing import Tuple
from textwrap import wrap

DICT_MAPPER = {
    1: "A",  2: "B",  3: "C",  4: "D",
    5: "E",  6: "F",  7: "G",  8: "H",
    9: "I",  10: "J", 11: "K", 12: "L",
    13: "M", 14: "N", 15: "O", 16: "P",
    17: "Q", 18: "R", 19: "S", 20: "T",
    21: "U", 22: "V", 23: "W", 24: "X",
    25: "Y", 26: "Z", 32: "_", 48: 0,
    49: 1,   50: 2,   51: 3,   52: 4,
    53: 5,   54: 6,   55: 7,   56: 8,
    57: 9,
}


def find(sock: socket, signature: bytes, retry: int = 1) -> Tuple[bytes, bool]:
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


def crc(msg: int) -> Tuple[int, bool]:
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
