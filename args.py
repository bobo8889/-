from argparse import ArgumentParser


class Arguments:
    """命令行解析类

    从命令行中解析参数，便于在后续将解析出的参数交由其他模块处理

    Attributes:
        path: 配置文件路径
    """

    path: str

    def parse(self) -> None:
        """解析命令行参数

        从命令行读取指定的参数，将参数保存到类属性中

        Returns:
            None
        """
        parser = ArgumentParser()
        parser.add_argument(
            "--config",
            type=str,
            default="./config.json",
            help="path to config file",
        )
        args = parser.parse_args()
        self.path = args.config
