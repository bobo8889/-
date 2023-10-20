from asyncio import sleep
from typing import Callable
from model.adsb import ADSBPacket


class Publisher:
    """ADS-B 数据发布者

    用于发布 ADS-B 数据至订阅者

    Attributes:
        packet: ADS-B 报文共享缓冲区
        prev_ts: 上一次发布的时间戳
    """

    def __init__(self, packet: ADSBPacket) -> None:
        self.packet = packet
        self.prev_ts = packet.ts

    async def subscribe(self, subscriber: Callable) -> None:
        while True:
            if self.packet.ts != self.prev_ts:
                await subscriber(self.packet)
                self.prev_ts = self.packet.ts
            await sleep(0.05)
