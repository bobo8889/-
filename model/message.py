from model.response import ResponseData, Response
from datetime import datetime, timezone


def set_message(path: str, message: str, data: ResponseData) -> Response:
    """生成响应消息

    该函数将为服务器生成统一的响应消息

    Args:
        path (str): 请求路径
        message (str): 响应消息
        data (ResponseData): 响应数据

    Returns:
        Response: 响应对象
    """
    return Response(
        time=datetime.now(tz=timezone.utc).isoformat(
            timespec="seconds"
        ).replace("+00:00", "Z"),
        status=200, error=False, path=path, message=message, data=data
    )
