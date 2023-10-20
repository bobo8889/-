from model.response import ResponseData, Response
from datetime import datetime, timezone


def set_message(path: str, message: str, data: ResponseData) -> Response:
    """Generate message

    This function will generate unified message for the server

    Args:
        path (str): Request path
        message (str): Message text
        data (ResponseData): Response data

    Returns:
        Response: Response object
    """
    return Response(
        time=datetime.now(tz=timezone.utc).isoformat(
            timespec="seconds"
        ).replace("+00:00", "Z"),
        status=200, error=False, path=path, message=message, data=data
    )
