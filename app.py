from socket import socket, AF_INET, SOCK_STREAM
from signal import signal, SIGINT
from sys import exit


def graceful_shutdown(socket: socket):
    socket.close()
    exit(0)


def main():
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(("172.17.138.214", 30002))
    signal(SIGINT, lambda *_: graceful_shutdown(sock))

    while True:
        buffer = sock.recv(128)
        print(buffer.decode("utf-8"))


if __name__ == '__main__':
    main()
