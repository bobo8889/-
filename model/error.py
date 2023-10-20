from model.response import ResponseData, Response
from datetime import datetime, timezone


def set_error(path: str, message: str, status: int, data: ResponseData) -> Response:
    """Generate error message

    This function will generate unified error message for the server

    Args:
        path (str): Request path
        message (str): Message text
        status (int): HTTP status code
        data (ResponseData): Response data

    Returns:
        Response: Response object
    """
    return Response(
        time=datetime.now(tz=timezone.utc).isoformat(
            timespec="seconds"
        ).replace("+00:00", "Z"),
        status=status, error=True, path=path, message=message, data=data
    )
