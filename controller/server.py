from typing import Callable, Tuple
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException, Request, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from config.router import API_PREFIX, API_VERSION
from model.router import RouterItem
from model.error import set_error
from uvicorn import run
from fastapi.openapi.utils import get_openapi
from starlette.exceptions import HTTPException as StarletteHTTPException


class Server:
    """FastAPI 包装器

    此类将使用 FastAPI 创建一个服务器实例并处理路由

    Attributes:
        host (str): 绑定的主机地址
        port (int): 绑定的端口号
        cors (bool): 是否启用 CORS
        debug (bool): 是否启用调试模式
    """

    def __init__(self, host: str, port: str, cors=False, debug=False) -> None:
        debug_url = f"{API_PREFIX}/{API_VERSION}/devel" if debug else None
        self.app = FastAPI(docs_url=debug_url, redoc_url=debug_url)
        if cors:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_methods=["*"],
                allow_headers=["*"],
                allow_credentials=True,
            )
        self.host, self.port = host, int(port)
        self.cors, self.debug = cors, debug

    def route(self, conf: RouterItem, *args: Tuple) -> None:
        """注册路由

        此方法将向 Server 实例注册一个路由

        Args:
            conf (RouterItem): 路由配置，模型来自 config/routers.py
            *args (tuple): 传入路由处理函数的额外参数，用于避免全局变量

        Returns:
            None
        """
        method_mapping = {
            "get": self.app.get,
            "post": self.app.post,
            "put": self.app.put,
            "delete": self.app.delete,
            "patch": self.app.patch,
            "options": self.app.options,
            "head": self.app.head,
            "trace": self.app.trace,
            "websocket": self.app.websocket,
        }
        tags = conf.get("tags")
        model = conf.get("model")
        router = conf.get("router")
        handler = conf.get("handler")
        summary = conf.get("summary")
        method = conf.get("method").lower()
        description = conf.get("description")
        dependencies = conf.get("dependencies")
        if method not in method_mapping:
            raise ValueError(f"Invalid method: {method}")
        dependencies = list(set(dependencies))

        if method != "websocket":
            @method_mapping[method](
                router, response_model=model["response"],  summary=summary,
                description=description, dependencies=dependencies, tags=tags,
            )
            def _(req: model["request"] = None):
                return handler(req, conf, *args)
        else:
            @method_mapping[method](
                router, dependencies=dependencies,
            )
            async def _(ws: model["request"] = WebSocket):
                return await handler(ws, conf, *args)

    def on(self, event: str, callback: Callable) -> None:
        """注册事件回调

        此方法将向服务器实例注册一个事件处理程序
        该方法常用于注册 Ctrl + C 事件

        Args:
            event (str): FastAPI 内建事件名称
            callback (Callable): 事件处理函数

        Returns:
            None
        """
        @self.app.on_event(event)
        def _():
            callback()

    def info(self, title: str, description: str, version: str):
        """设置 Swagger 信息

        该方法将设置 Swagger 信息，包括标题、描述和基础 URL

        Args:
            title (str): Swagger 标题
            description (str): Swagger 描述
            base_url (str): API 基础 URL
        """
        self.app.title = title
        self.app.description = description
        self.app.version = version

    def static(self, path: str, dir: str, html: bool = True) -> None:
        """注册静态网页目录

        该方法将向服务器实例注册一个静态网站目录

        Args:
            path (str): 静态网站目录的路由
            dir (str): 静态网站目录资源文件路径
            html (bool): 是否设定默认文档为 index.html

        Returns:
            None
        """
        self.app.mount(path, StaticFiles(directory=dir, html=html), name=dir)

    def start(self) -> None:
        """启动 FastAPI 服务器

        该方法将覆盖默认的异常处理程序并启动服务器
        此方法还会从 Swagger UI 中删除 422 错误

        Returns:
            None
        """
        @self.app.exception_handler(StarletteHTTPException)
        async def _(req: Request, exc: HTTPException) -> JSONResponse:
            return JSONResponse(
                status_code=exc.status_code,
                content=set_error(
                    req.url.path, exc.detail,
                    exc.status_code, None
                ).model_dump()
            )

        @self.app.exception_handler(RequestValidationError)
        async def _(req: Request, _) -> JSONResponse:
            return JSONResponse(
                status_code=400,
                content=set_error(
                    req.url.path,
                    "Validation error",
                    400, None
                ).model_dump()
            )

        if not self.app.openapi_schema:
            self.app.openapi_schema = get_openapi(
                title=self.app.title,
                version=self.app.version,
                description=self.app.description,
                routes=self.app.routes,
            )
            for _, method_item in self.app.openapi_schema.get("paths").items():
                for _, param in method_item.items():
                    responses = param.get("responses")
                    if "422" in responses:
                        del responses["422"]

        run(self.app, host=self.host, port=self.port, server_header=False)
