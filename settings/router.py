
from typing import List
from fastapi import WebSocket
from model.router import RouterItem
from endpoint.socket import socket_handler

API_PREFIX = "/api"
API_ROUTERS: List[RouterItem] = [
    {
        "tags": [],
        "router": f"{API_PREFIX}/socket",
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
