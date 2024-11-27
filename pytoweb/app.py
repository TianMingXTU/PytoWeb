"""
PytoWeb应用主类
"""

from typing import Optional, Any, Callable
from .server import Server
from .router import Router
from .components import Component
from .vdom import VDOMRenderer
import logging

class App:
    """PytoWeb应用主类"""
    
    def __init__(self):
        self.server = Server()
        self.router: Optional[Router] = None
        self.root: Optional[Component] = None
        self.renderer = VDOMRenderer()
        self.middleware = []
        self._logger = logging.getLogger(__name__)
        
    def use(self, middleware: Any):
        """添加中间件"""
        if isinstance(middleware, Router):
            self.router = middleware
        else:
            self.middleware.append(middleware)
            
    def mount(self, component: Component):
        """挂载根组件"""
        self.root = component
        
    def render(self, component: Component) -> str:
        """渲染组件"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>PytoWeb App</title>
            <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
        </head>
        <body>
            {self.renderer.create_element(component)}
        </body>
        </html>
        """
        
    def handle_request(self, handler: Callable, *args, **kwargs) -> str:
        """处理请求并渲染响应"""
        try:
            # 调用路由处理器
            result = handler(*args, **kwargs)
            
            # 如果返回的是组件，渲染它
            if isinstance(result, Component):
                return self.render(result)
            
            # 否则直接返回结果
            return str(result)
        except Exception as e:
            self._logger.error(f"Error handling request: {e}", exc_info=True)
            raise
        
    def run(self, host: str = "localhost", port: int = 8000, debug: bool = False):
        """启动应用"""
        if debug:
            logging.basicConfig(level=logging.DEBUG)
            
        self._logger.info(f"Starting PytoWeb app on http://{host}:{port}")
        
        # 注册路由处理器
        if self.router:
            for route in self.router.routes:
                # 包装路由处理器
                wrapped_handler = lambda *args, **kwargs: self.handle_request(route.handler, *args, **kwargs)
                self.server.add_route(route.path, wrapped_handler)
                
        # 注册中间件
        for middleware in self.middleware:
            self.server.use(middleware)
            
        # 启动服务器
        try:
            self.server.run(host, port)
        except Exception as e:
            self._logger.error(f"Error starting server: {e}", exc_info=True)
            raise
