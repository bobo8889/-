from datetime import datetime
from logging import Logger, getLogger
from logging.config import dictConfig
from config.router import API_ROUTERS
from controller.adsb import is_crc_valid, is_message_decodable
from socket import socket, AF_INET, SOCK_STREAM
from config.logger import LOGGER_CONFIG
from config.settings import Settings
from controller.arguments import Arguments
from controller.publisher import Publisher
from controller.server import Server
from controller.utils import find
from _thread import start_new_thread
from sys import exit
from model.adsb import ADSBPacket


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


def adsb_decoder(sock: socket, packet: ADSBPacket) -> None:
    """从 Socket 中读取并解析报文

    Args:
        sock (socket): 创建好的已打开的 socket 实例
        packet (ADSBPacket): ADS-B 报文缓冲区

    Returns:
        None
    """
    while True:
        # 取得报文头部 *，长度为 1 字节
        _, err = find(sock, b"*")
        if err:
            continue
        # 接收剩余报文内容并检查完整性
        data_recv = sock.recv(29)
        if data_recv[-1:] != b";":
            continue
        msg = data_recv[:-1].decode("utf-8")
        # 检查 Downlink Format，判断是否可解码
        df, decodable = is_message_decodable(msg)
        if not decodable:
            continue
        # Downlink Format 为 17 时需 CRC 校验
        if df == 17 and not is_crc_valid(msg):
            continue
        # 赋值报文和时间戳
        packet.msg = msg
        packet.ts = int(datetime.now().timestamp() * 1000)


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

    # 连接报文服务器
    source_host, source_port = conf.source.host, conf.source.port
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((source_host, source_port))
    logger.info(f"Connected to {source_host}:{source_port}")

    # 启动报文解析线程，创建发布者
    packet = ADSBPacket()
    publisher = Publisher(packet)
    start_new_thread(adsb_decoder, (sock, packet))

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
    for router in API_ROUTERS:
        server.route(router, publisher)

    # 启动 HTTP 服务器线程
    server.start()


if __name__ == '__main__':
    main()
