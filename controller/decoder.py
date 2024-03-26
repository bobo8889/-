from datetime import datetime
from time import sleep
from typing import List, Tuple
from controller.database import Database
import library as pms
from model.database.records import Records
from _thread import start_new_thread

TIMEUNIT_SECOND = 1000
BUFFER_TIMEOUT = 10*TIMEUNIT_SECOND

PLACEHOLDER_NUMBER = -9999
PLACEHOLDER_STRING = "N/A"


class ADSBDecoderBuffer:
    icao: str
    message: str
    typecode: int
    timestamp: int

    def __init__(self, icao: str, message: str, typecode: int, timestamp: int):
        self.icao = icao
        self.message = message
        self.typecode = typecode
        self.timestamp = timestamp


class ADSBDecoder:
    """ADS-B 报文解码器

    从 ADS-B 报文中解析出各种资讯

    Attributes:
        msg (str): 原始报文
    """

    tc: int
    ts: int
    msg: str

    archiving_enabled = True

    queue: List[ADSBDecoderBuffer] = []
    buffer: List[ADSBDecoderBuffer] = []

    def __init__(self, db: Database = None) -> None:
        if db is not None:
            self.archiving_thread = start_new_thread(self.__update_database__, (db,))

    def __del__(self):
        self.archiving_enabled = False

    def __update_database__(self, db: Database) -> None:
        """数据库更新线程

        扫描存档队列，将队列中的报文存入数据库

        Args:
            db (Database): _description_
        """
        while self.archiving_enabled:
            if len(self.queue) > 0:
                record = Records().set_attrs({
                    "timestamp": self.queue[0].timestamp,
                    "message": self.queue[0].message,
                    "typecode": self.queue[0].typecode,
                    "icao": self.queue[0].icao,
                })
                self.queue.pop(0)
                db.insert(record)
            sleep(0.1)

    def update_queue(self):
        """更新数据库存档队列

        将当前报文加入数据库存档队列

        Returns:
            None
        """
        self.queue.append(ADSBDecoderBuffer(
            icao=self.get_icao(),
            message=self.msg,
            typecode=self.tc,
            timestamp=self.ts,
        ))

    def update_buffer(self):
        """更新缓冲区

        将当前报文加入缓冲区并更新数据库
        若缓冲区时间戳超时，将超时报文移除

        Returns:
            List[ADSBDecoderBuffer]: 缓冲区
        """
        self.buffer.append(ADSBDecoderBuffer(
            icao=self.get_icao(),
            message=self.msg,
            typecode=self.tc,
            timestamp=self.ts,
        ))
        current_ts = int(datetime.now().timestamp() * 1000)
        for i in self.buffer:
            if current_ts - i.timestamp > BUFFER_TIMEOUT:
                self.buffer.remove(i)

    def parse_typecode(self):
        """解析报文类型码

        解析报文类型码，若解码失败，报文类型码为 PLACEHOLDER_NUMBER

        Returns:
            None
        """
        tc = pms.adsb.typecode(self.msg)
        if tc is None:
            self.tc = PLACEHOLDER_NUMBER
        else:
            self.tc = tc

    def parse_timestamp(self) -> int:
        """设定时间戳

        将当前时间戳设定属性 ts 中

        Returns:
            None
        """
        self.ts = int(datetime.now().timestamp() * 1000)

    def get_icao(self) -> str:
        """取得 ICAO 数据

        取得 ICAO 数据，若解码失败，返回的 ICAO 数据为 PLACEHOLDER_STRING

        Returns:
            str: ICAO 数据
        """
        if len(self.msg) == 0:
            return PLACEHOLDER_STRING
        return self.msg[2:8]

    def get_callsign(self) -> str:
        """取得呼号

        取得呼号，若解码失败，返回的呼号为 PLACEHOLDER_STRING

        Returns:
            str: 呼号
        """
        if self.tc < 1 or self.tc > 4:
            return PLACEHOLDER_STRING
        return pms.adsb.callsign(self.msg)

    def get_altitude(self) -> int:
        """取得高度

        取得高度，若解码失败，返回的高度为 PLACEHOLDER_NUMBER

        Returns:
            int: 高度
        """
        if self.tc < 5 or self.tc > 18:
            return PLACEHOLDER_NUMBER
        return pms.adsb.altitude(self.msg)

    def get_heading(self) -> float:
        """取得航向

        取得航向，若解码失败，返回的航向为 PLACEHOLDER_NUMBER

        Returns:
            float: 航向
        """
        hd = pms.commb.hdg60(self.msg)
        if hd is None:
            return PLACEHOLDER_NUMBER
        return hd

    def get_velocity(self) -> float:
        """取得速度

        取得速度，若解码失败，返回的速度为 PLACEHOLDER_NUMBER

        Returns:
            float: 速度
        """
        if self.tc == 19:
            v = pms.adsb.velocity(self.msg)[0]
            if v is not None:
                return v
        return PLACEHOLDER_NUMBER

    def get_position(self) -> Tuple[float, float]:
        """取得位置

        从报文中取得位置，若解码失败，返回的位置为 (PLACEHOLDER_NUMBER, PLACEHOLDER_NUMBER)

        Returns:
            Tuple[float, float]: 纬度，经度
        """
        def is_pos_available(tc):
            return 5 <= tc <= 8 or 9 <= tc <= 18 or 20 <= tc <= 22
        if is_pos_available(self.tc):
            odd = pms.adsb.oe_flag(self.msg)
            for i in self.buffer:
                if is_pos_available(i.typecode) and i.icao == self.get_icao() and pms.adsb.oe_flag(i.message) != odd:
                    result = pms.adsb.position(
                        i.message,
                        self.msg,
                        i.timestamp,
                        self.ts,
                    )
                    if result is not None:
                        return result

        return PLACEHOLDER_NUMBER, PLACEHOLDER_NUMBER
