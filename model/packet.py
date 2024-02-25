class ADSBPacket:
    """ADS-B 数据包

    Attributes:
        icao (str): ICAO 地址
        message (str): 原始报文
        callsign (str): 机载编号
        status (str): 飞行状态
        altitude (int): 海拔高度
        timestamp (int): 毫秒时间戳
        heading (float): 航向
        velocity (float): 速度
        latitude (float): 纬度
        longitude (float): 经度
    """
    icao: str = ""
    message: str = ""
    callsign: str = ""
    status: str = ""
    altitude: int = 0
    timestamp: int = 0
    heading: float = 0
    velocity: float = 0
    latitude: float = 0.0
    longitude: float = 0.0
