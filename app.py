from adsb import is_crc_valid, is_message_decodable
from socket import socket, AF_INET, SOCK_STREAM
from signal import signal, SIGINT
from pyModeS.decoder import tell
from settings import Settings
from args import Arguments
from logger import println
from typing import Tuple
from utils import find
from sys import exit


def graceful_shutdown(sock: socket) -> None:
    """优雅关闭 TCP 连接

    收到系统信号 SIGINT 时，关闭 TCP 连接并退出程序

    Args:
        sock (socket): 创建好的 socket 实例

    Returns:
        None
    """
    sock.close()
    print(end="\r")
    println("TCP connection has been closed")
    exit(0)


def parse_message(sock: socket) -> Tuple[str, bool]:
    """从 Socket 中读取并解析报文

    Args:
        sock (socket): 创建好的 socket 实例

    Returns:
        Tuple[str, bool]: 报文内容，是否解析失败
    """
    # 取得报文头部 *，长度为 1 字节
    _, err = find(sock, b"*")
    if err:
        return "", True
    # 接收剩余报文内容并检查完整性
    buffer = sock.recv(29)
    if buffer[-1:] != b";":
        return "", True
    # 报文转成字符串并返回最终结果
    return buffer[:-1].decode("utf-8"), False


def main():
    # 解析命令行参数
    args = Arguments()
    args.parse()

    # 解析配置文件
    conf = Settings()
    conf.parse(args.path)

    # 连接报文服务器
    source_host = conf.source.host
    source_port = conf.source.port
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((source_host, source_port))

    # 注册系统信号处理函数
    signal(SIGINT, lambda *_: graceful_shutdown(sock))

    while True:
        # 读取、解析报文，判断合法性
        msg, err = parse_message(sock)
        if err:
            continue
        # 检查 Downlink Format，判断是否可解码
        df, decodable = is_message_decodable(msg)
        if not decodable:
            continue
        # Downlink Format 为 17 时需 CRC 校验
        if df == 17 and not is_crc_valid(msg):
            continue
        # 打印报文内容
        println(f"packet received: {msg}")
        tell(msg)


if __name__ == '__main__':
    main()
