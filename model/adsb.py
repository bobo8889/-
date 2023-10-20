class ADSBPacket:
    """ADS-B 数据包
    
    Attributes:
        ts: 时间戳（毫秒）
        msg: ADS-B 消息
    """
    ts: int
    msg: str

    def __init__(self) -> None:
        self.ts = 0
        self.msg = ""
