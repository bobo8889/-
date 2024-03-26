from typing import Any, List, Optional
from pydantic import BaseModel, Field
from controller.database import Database
from controller.decoder import ADSBDecoder
from controller.publisher import Publisher
from model.database.records import Records
from model.message import set_message
from model.packet import ADSBPacket
from model.response import Response
from model.router import RouterItem


class QueryRequest(BaseModel):
    start: int = Field(
        title="历史查询起始时间", description="Unix 时间戳格式，精确到 ms",
    )
    end: int = Field(
        title="历史查询截止时间", description="Unix 时间戳格式，精确到 ms"
    )


class QueryResponse(Response):
    data: Optional[List[Any]] = Field(
        title="结果", description="操作或查询结果"
    )


def query_handler(req: QueryRequest, router: RouterItem, database: Database, __publisher__: Publisher) -> QueryResponse:
    records = database.query(
        Records,
        Records.timestamp >= req.start,
        Records.timestamp <= req.end,
    )
    
    data_packets = []
    decoder = ADSBDecoder()
    
    for record in records:
        data = record.get_attrs()
        decoder.msg = data.get("message")
        decoder.ts = data.get("timestamp")
        decoder.tc = data.get("typecode")
        # 解析报文
        packet = ADSBPacket()
        packet.icao = decoder.get_icao()
        packet.callsign = decoder.get_callsign()
        packet.altitude = decoder.get_altitude()
        packet.heading = decoder.get_heading()
        packet.velocity = decoder.get_velocity()
        packet.latitude, packet.longitude = decoder.get_position()
        # 为数据打上时标
        packet.message = decoder.msg
        packet.timestamp = decoder.ts
        data_packets.append(packet.__dict__)
    return set_message(router["router"], "成功获取数据", data_packets)
