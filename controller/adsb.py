from re import sub
from typing import Tuple
from controller.utils import crc


def is_message_valid(msg: str) -> bool:
    """判断报文合法性

    Args:
        msg (str): ADS-B 完整报文

    Returns:
        bool: 报文长度是否正确，正确返回 True，否则返回 False
    """
    return len(sub(r'[^A-Za-z0-9]', "", msg)) == 28


def is_message_decodable(msg: str) -> Tuple[int, bool]:
    """透过 Downlink Format 判断报文是否可解码

    Args:
        msg (str): ADS-B 完整报文

    Returns:
        Tuple[int, bool]: Downlink Format，报文是否可解码
    """
    df = int(msg[:2], 16) >> 3
    """
    Downlink Format (DF) 说明
    17: ADS-B 1090 Extended Squitter (ADS-B)
    18: TIS-B, cannot be interrogated
    20: Mode-S Comm-B Altitude (Altitude)
    21: Mode-S Comm-B Identity (Squawk code)
    """
    return df, df == 17 or df == 20 or df == 21


def is_crc_valid(msg: str) -> bool:
    """判断报文 CRC 校验是否通过

    Args:
        msg (str): ADS-B 完整报文

    Returns:
        bool: 报文 CRC 校验是否通过，通过返回 True，否则返回 False
    """
    result, err = crc(msg)
    return not err and result == 0  # CRC 校验码须为 0
