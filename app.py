from logging import Logger, getLogger
from logging.config import dictConfig
from typing import Tuple
from controller.database import Database
from model.database.records import Records
from settings.router import API_ROUTERS
from socket import socket, AF_INET, SOCK_STREAM
from settings.logger import LOGGER_CONFIG
from settings.settings import Settings
from controller.arguments import Arguments
from controller.publisher import Publisher
from controller.server import Server
from controller.decoder import ADSBDecoder
from _thread import start_new_thread
from sys import exit
from model.packet import ADSBPacket


def graceful_shutdown(sock: socket, logger: Logger) -> None:
    """优雅关闭 TCP 连接

    收到系统信号 SIGINT 时，关闭 TCP 连接

    Args:
        sock (socket): 创建好的 socket 实例
        logger (Logger): 创建好的日志记录器

    Returns:
        None
    """
    sock.close()
    logger.info("TCP connection has been closed")


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
        try:
            data = sock.recv(len(signature))
            if data.startswith(signature):
                return data, False
        except:
            return b"", True

    return b"", True


def decoder_daemon(db: Database, sock: socket, decoder: ADSBDecoder, packet: ADSBPacket) -> None:
    """从 Socket 中读取并解析报文

    Args:
        sock (socket): 创建好的已打开的 socket 实例
        packet (ADSBPacket): ADS-B 报文缓冲区

    Returns:
        None
    """
    while True:
        # 取得报文头部 *，长度为 1 字节
        _, err = socket_find(sock, b"*")
        if err:
            continue
        # 接收剩余报文内容并检查完整性
        data_recv = sock.recv(29)
        if data_recv[-1:] != b";":
            continue
        # 设定报文
        decoder.msg = data_recv[:-1].decode("utf-8")
        decoder.parse_typecode()
        decoder.parse_timestamp()
        # 解析报文
        packet.icao = decoder.get_icao()
        packet.callsign = decoder.get_callsign()
        packet.altitude = decoder.get_altitude()
        packet.heading = decoder.get_heading()
        packet.velocity = decoder.get_velocity()
        packet.latitude, packet.longitude = decoder.get_position()
        # 为数据打上时标
        packet.message = decoder.msg
        packet.timestamp = decoder.ts
        # 收尾工作
        decoder.update_buffer()
        decoder.update_queue()


def connect_tcpserver(host: str, port: int, timeout: int) -> Tuple[socket, bool]:
    """连接 TCP 服务器

    Args:
        host (str): 服务器地址
        port (int): 服务器端口
        timeout (int): 连接超时时间

    Returns:
        Tuple[socket, bool]: 已连接的 socket 实例，连接是否失败
    """
    sock = socket(AF_INET, SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        return sock, False
    except:
        return sock, True


def main():
    # 取得全局日志记录器
    dictConfig(LOGGER_CONFIG)
    logger = getLogger("global_logger")

    # 解析命令行参数
    args = Arguments()
    args.parse()

    # 解析配置文件
    conf = Settings()
    err = conf.parse(args.path)
    if err:
        logger.info("Failed to parse config")
        exit(1)

    # Connect to database
    db = Database(
        engine=conf.database.engine,
        db_name=conf.database.database,
        username=conf.database.username,
        password=conf.database.password,
        host=conf.database.host,
        port=conf.database.port,
        tables=[Records],
    )
    err = db.connect()
    if err:
        logger.info("Failed to connect to database")
        return

    # Migrating database
    logger.info("Migrating database")
    db.migrate()

    # 连接报文服务器
    logger.info("Connecting to ADS-B server...")
    source_host, source_port = conf.source.host, conf.source.port
    sock, err = connect_tcpserver(
        source_host, source_port,
        conf.source.timeout,
    )
    if err:
        logger.info(f"Failed to connect to {source_host}:{source_port}")
        exit(1)
    logger.info(f"Connected to {source_host}:{source_port}")

    # 启动报文解析线程，创建发布者
    decoder = ADSBDecoder(db)
    packet = ADSBPacket()
    start_new_thread(decoder_daemon, (db, sock, decoder, packet,))

    # 创建 HTTP 服务器
    server_host, server_port = conf.server.host, conf.server.port
    server_cors, server_debug = conf.server.cors, conf.server.debug
    server = Server(
        host=server_host, port=server_port,
        cors=server_cors, debug=server_debug,
    )
    # 注册系统信号处理函数
    server.on("shutdown", lambda: graceful_shutdown(sock, logger))

    # 注册 API 路由
    publisher = Publisher(packet)
    for router in API_ROUTERS:
        server.route(router, db, publisher)
    # 启动地图瓦片服务
    server.static(path="/", dir="./view")

    # 启动 HTTP 服务器线程
    server.start()


if __name__ == '__main__':
    main()
