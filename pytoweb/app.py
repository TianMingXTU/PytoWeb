"""
PytoWeb应用主类
"""

from __future__ import annotations
from typing import Optional, Any, Callable, List, Dict, Union, TypeVar, TYPE_CHECKING
from dataclasses import dataclass
from .server import Server
from .router import Router
from .components import Component
from .vdom import VDOMRenderer
import logging
import sys
import traceback
from http import HTTPStatus

if TYPE_CHECKING:
    from .middleware import Middleware

T = TypeVar('T', bound='App')

class AppError(Exception):
    """PytoWeb应用异常基类"""
    pass

@dataclass
class AppConfig:
    """应用配置"""
    host: str = "localhost"
    port: int = 8000
    debug: bool = False
    static_dir: str = "static"
    template_dir: str = "templates"
    secret_key: Optional[str] = None

class App:
    """PytoWeb应用主类"""
    
    def __init__(self, config: Optional[AppConfig] = None):
        """初始化应用"""
        try:
            self.config = config or AppConfig()
            self.server = Server(self.config.host, self.config.port)
            self.router = Router()
            self.root: Optional[Component] = None
            self.renderer = VDOMRenderer()
            self._logger = logging.getLogger(__name__)
            
            # 配置日志
            if self.config.debug:
                logging.basicConfig(
                    level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                
            # 设置静态文件目录
            self.server.static_dir = self.config.static_dir
            
            # 注册默认路由处理器
            self.router.add('/', self._handle_root)
            self.server.add_route('/', self.router.dispatch)
            
        except Exception as e:
            raise AppError(f"Failed to initialize application: {e}") from e
            
    def _handle_root(self, request: Dict[str, Any]) -> str:
        """处理根路由请求"""
        print("[DEBUG] Handling root request")
        if self.root is None:
            raise AppError("No root component mounted")
        try:
            html = self.render(self.root)
            print(f"[DEBUG] Generated HTML length: {len(html)}")
            return html
        except Exception as e:
            print(f"[DEBUG] Error rendering root: {e}")
            raise AppError(f"Failed to render root: {e}") from e
            
    def mount(self: T, component: Component) -> T:
        """挂载根组件"""
        try:
            if not isinstance(component, Component):
                raise AppError("Component must be an instance of Component")
            self.root = component
            return self
        except Exception as e:
            if isinstance(e, AppError):
                raise
            raise AppError(f"Failed to mount component: {e}") from e
        
    def render(self, component: Component) -> str:
        """渲染组件"""
        try:
            if not isinstance(component, Component):
                raise AppError("Component must be an instance of Component")
                
            vdom = component.render()
            html = self.renderer.render_to_string(vdom)
            
            return f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>PytoWeb App</title>
                <style>{self._get_styles()}</style>
                <script>{self._get_scripts()}</script>
            </head>
            <body>
                <div id="app">{html}</div>
            </body>
            </html>
            """
        except Exception as e:
            if isinstance(e, AppError):
                raise
            raise AppError(f"Failed to render component: {e}") from e
            
    def _get_styles(self) -> str:
        """获取应用样式"""
        try:
            from .styles import get_global_styles
            return get_global_styles()
        except Exception as e:
            self._logger.error(f"Failed to get styles: {e}")
            return ""
            
    def _get_scripts(self) -> str:
        """获取应用脚本"""
        try:
            from .events import get_client_script
            return get_client_script()
        except Exception as e:
            self._logger.error(f"Failed to get scripts: {e}")
            return ""
            
    def run(self, host: str = "127.0.0.1", port: int = 8000, debug: bool = False):
        """运行应用"""
        try:
            if debug:
                self._logger.setLevel(logging.DEBUG)
            self.server.run(host, port)
        except Exception as e:
            raise AppError(f"Failed to run application: {e}") from e
