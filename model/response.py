from pydantic import BaseModel
from typing import Union, List, Dict

ResponseData = Union[
    int,
    str,
    float,
    bool,
    Dict,
    List,
    BaseModel,
    None,
]


class Response(BaseModel):
    time: str
    status: int
    error: bool
    path: str
    message: str
    data: ResponseData
