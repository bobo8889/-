from model.response import ResponseData, Response
from datetime import datetime, timezone


def set_error(path: str, message: str, status: int, data: ResponseData) -> Response:
    """生成错误消息

    该函数将为服务器生成统一的错误消息

    Args:
        path (str): 请求路径
        message (str): 错误消息
        status (int): HTTP 状态码
        data (ResponseData): 响应数据

    Returns:
        Response: 响应对象
    """
    return Response(
        time=datetime.now(tz=timezone.utc).isoformat(
            timespec="seconds"
        ).replace("+00:00", "Z"),
        status=status, error=True, path=path, message=message, data=data
    )
