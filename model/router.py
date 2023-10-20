from typing import Any, Callable, List
from model.response import Response
from pydantic import BaseModel


class RouterItemModal:
    response: Response
    request: BaseModel


class RouterItem:
    router: str
    method: str
    summary: str
    description: str
    tags: List[str]
    handler: Callable
    model: RouterItemModal
    dependencies: List[Any]
