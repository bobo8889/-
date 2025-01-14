from fastapi import WebSocket
from controller.database import Database
from controller.publisher import Publisher
from model.packet import ADSBPacket
from model.router import RouterItem


async def socket_handler(ws: WebSocket, __router__: RouterItem, __database__: Database, publisher: Publisher) -> None:
    """Websocket 处理回调

    用于处理 Websocket 连接请求，订阅 ADS-B 数据并将数据推送至客户端

    Args:
        ws (WebSocket): WebSocket 连接对象，由 FastAPI 自动传入
        router (RouterItem): 路由配置，模型来自 config/routers.py
        publisher (Publisher): ADS-B 报文发布者，用于订阅 ADS-B 数据

    Returns:
        None
    """
    try:
        async def subscriber(packet: ADSBPacket) -> None:
            """ADS-B 数据订阅者

            从 Publisher 订阅 ADS-B 报文消息

            Args:
                packet (ADSBPacket): ADS-B 报文共享缓冲区

            Returns:
                None
            """
            await ws.send_json(packet.__dict__)
        await ws.accept()
        await publisher.subscribe(subscriber)
    except:
        try:
            await ws.close()
        except:
            return
