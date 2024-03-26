from dataclasses import dataclass
from json import load


@dataclass
class Source:
    host: str
    port: str
    timeout: float


@dataclass
class Database:
    host: str
    port: str
    engine: str
    database: str
    username: str
    password: str


@dataclass
class Server:
    host: str
    port: str
    cors: bool
    debug: bool


@dataclass
class Settings:
    """全局配置类

    从指定 JSON 格式文件读取配置，用作应用全局配置

    Attributes:
        source (Source): 数据源配置
        server (Server): 服务器配置
    """

    source: Source = None
    server: Server = None
    database: Database = None

    def parse(self, path: str) -> bool:
        """打开并解析配置文件

        Args:
            path (str): JSON 格式配置文件路径

        Returns:
            bool: 返回 True 则表示解析失败，否则解析成功
        """
        try:
            f = open(path, "r")
            config_data = load(f)
            f.close()
            self.source = Source(
                **config_data.get("source_settings")
            )
            self.server = Server(
                **config_data.get("server_settings")
            )
            self.database = Database(
                **config_data.get("database_settings")
            )
            return False
        except:
            return True
