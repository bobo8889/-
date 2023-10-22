class ADSBPacket:
    """ADS-B 数据包

    Attributes:
        icao (str): ICAO 地址
        message (str): 原始报文
        callsign (str): 机载编号
        altitude (int): 海拔高度
        timestamp (int): 毫秒时间戳
    """

    icao: str = ""
    message: str = ""
    callsign: str = ""
    altitude: int = 0
    timestamp: int = 0
