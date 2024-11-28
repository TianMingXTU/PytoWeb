"""
PytoWeb路由模块
"""

from __future__ import annotations
from typing import Dict, List, Callable, Any, Optional, Union, TypeVar, TYPE_CHECKING
from dataclasses import dataclass
import re
import logging
from http import HTTPStatus

class RouterError(Exception):
    """路由错误"""
    pass

@dataclass
class Route:
    """路由定义类"""
    path: str
    handler: Callable[..., Any]
    methods: List[str]
    name: Optional[str] = None

    def __post_init__(self):
        """验证路由参数"""
        if not self.path.startswith('/'):
            raise RouterError(f"Path must start with '/': {self.path}")
        if not callable(self.handler):
            raise RouterError(f"Handler must be callable: {self.handler}")
        if not self.methods:
            self.methods = ['GET']
        self.methods = [m.upper() for m in self.methods]
        for method in self.methods:
            if method not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']:
                raise RouterError(f"Invalid HTTP method: {method}")

class Router:
    """路由管理器"""
    
    def __init__(self):
        self.routes: List[Route] = []
        self._logger = logging.getLogger(__name__)
        
    def add(self, path: str, handler: Callable[..., Any], methods: Optional[List[str]] = None, name: Optional[str] = None) -> Router:
        """添加路由"""
        try:
            route = Route(path, handler, methods or ['GET'], name)
            self.routes.append(route)
            return self
        except Exception as e:
            raise RouterError(f"Failed to add route: {e}") from e
        
    def route(self, path: str, methods: Union[List[str], str] = 'GET', name: Optional[str] = None) -> Callable:
        """通用路由装饰器"""
        if isinstance(methods, str):
            methods = [methods]
            
        def decorator(handler: Callable[..., Any]) -> Callable[..., Any]:
            self.add(path, handler, methods, name)
            return handler
        return decorator
        
    def get(self, path: str, name: Optional[str] = None) -> Callable:
        """装饰器：添加GET路由"""
        return self.route(path, ['GET'], name)
        
    def post(self, path: str, name: Optional[str] = None) -> Callable:
        """装饰器：添加POST路由"""
        return self.route(path, ['POST'], name)
        
    def put(self, path: str, name: Optional[str] = None) -> Callable:
        """装饰器：添加PUT路由"""
        return self.route(path, ['PUT'], name)
        
    def delete(self, path: str, name: Optional[str] = None) -> Callable:
        """装饰器：添加DELETE路由"""
        return self.route(path, ['DELETE'], name)
        
    def match(self, path: str, method: str = 'GET') -> Optional[Route]:
        """匹配路由"""
        method = method.upper()
        try:
            for route in self.routes:
                if method in route.methods:
                    # 简单路径匹配
                    if route.path == path:
                        return route
                        
                    # 参数路径匹配
                    pattern = re.sub(r'{\w+}', r'([^/]+)', route.path)
                    match = re.match(f'^{pattern}$', path)
                    if match:
                        return route
                        
            return None
        except Exception as e:
            self._logger.error(f"Route matching error: {e}")
            return None
        
    def url_for(self, name: str, **params: Any) -> str:
        """根据路由名称生成URL"""
        try:
            for route in self.routes:
                if route.name == name:
                    url = route.path
                    # 替换URL参数
                    for key, value in params.items():
                        placeholder = '{' + key + '}'
                        if placeholder not in url:
                            raise RouterError(f"Parameter '{key}' not found in route '{name}'")
                        url = url.replace(placeholder, str(value))
                    return url
                    
            raise RouterError(f"No route found with name '{name}'")
        except Exception as e:
            if isinstance(e, RouterError):
                raise
            raise RouterError(f"Failed to generate URL for route '{name}': {e}") from e
        
    def group(self, prefix: str) -> Router:
        """创建路由组"""
        if not prefix.startswith('/'):
            raise RouterError("Group prefix must start with '/'")
            
        group_router = Router()
        
        def add_group_route(path: str, handler: Callable[..., Any], methods: List[str], name: Optional[str] = None) -> None:
            full_path = prefix + path
            self.add(full_path, handler, methods, name)
            
        group_router.add = add_group_route
        return group_router
        
    def mount(self, prefix: str, router: Router) -> Router:
        """挂载其他路由器"""
        if not prefix.startswith('/'):
            raise RouterError("Mount prefix must start with '/'")
            
        try:
            for route in router.routes:
                full_path = prefix + route.path
                self.add(full_path, route.handler, route.methods, route.name)
            return self
        except Exception as e:
            raise RouterError(f"Failed to mount router at '{prefix}': {e}") from e
        
    def middleware(self, middleware_func: Callable[..., Any]) -> Router:
        """添加路由中间件"""
        original_routes = self.routes[:]
        for route in original_routes:
            original_handler = route.handler
            
            def wrapped_handler(*args, **kwargs):
                return middleware_func(original_handler, *args, **kwargs)
                
            route.handler = wrapped_handler
        return self

    def dispatch(self, request):
        """Dispatch the request to the appropriate handler"""
        path = request.path
        method = request.method
        
        # 查找匹配的路由
        handler = self.match(path, method)
        if handler:
            return handler.handler(request)
            
        # 没有找到路由
        return None
