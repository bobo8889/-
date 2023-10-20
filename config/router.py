
from typing import List
from fastapi import WebSocket
from model.router import RouterItem
from endpoint.socket import socket_handler


WEB_PREFIX = "/"
API_PREFIX = "/api"
API_VERSION = "v1"

API_ROUTERS: List[RouterItem] = [
    {
        "tags": [],
        "router": f"{API_PREFIX}/{API_VERSION}/socket",
        "method": "websocket",
        "model": {
            "request": WebSocket,
            "response": None,
        },
        "dependencies": [],
        "handler": socket_handler,
        "summary": "",
        "description": "",
    },
]
