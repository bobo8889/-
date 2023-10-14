import pyModeS as pms
from pyModeS.extra.tcpclient import TcpClient


class ADSBClient(TcpClient):
    def __init__(self, host: str, port: int, rawtype: str):
        super(ADSBClient, self).__init__(host, port, rawtype)

    def handle_messages(self, messages):
        for msg, ts in messages:
            # Wrong data length, not ADSB or CRC failed
            if len(msg) != 28 or pms.df(msg) != 17 or pms.crc(msg) != 0:
                continue

            icao = pms.adsb.icao(msg)
            tc = pms.adsb.typecode(msg)
            print(ts, icao, tc, msg)


def main():
    # Create new client with host and port as arguments
    client = ADSBClient(host='172.17.138.214', port=30002, rawtype='raw')
    client.run()


if __name__ == '__main__':
    main()
