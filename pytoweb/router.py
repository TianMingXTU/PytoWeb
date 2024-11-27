"""
PytoWeb路由模块
"""

from typing import Dict, List, Callable, Any, Optional, Union
from dataclasses import dataclass
import re
import logging

@dataclass
class Route:
    """路由定义类"""
    path: str
    handler: Callable
    methods: List[str] = None
    name: Optional[str] = None

class Router:
    """路由管理器"""
    
    def __init__(self):
        self.routes: List[Route] = []
        self._logger = logging.getLogger(__name__)
        
    def add(self, path: str, handler: Callable, methods: List[str] = None, name: str = None):
        """添加路由"""
        route = Route(path, handler, methods or ['GET'], name)
        self.routes.append(route)
        return self
        
    def route(self, path: str, methods: Union[List[str], str] = 'GET', name: str = None):
        """通用路由装饰器"""
        if isinstance(methods, str):
            methods = [methods]
            
        def decorator(handler: Callable):
            self.add(path, handler, methods, name)
            return handler
        return decorator
        
    def get(self, path: str, name: str = None):
        """装饰器：添加GET路由"""
        return self.route(path, ['GET'], name)
        
    def post(self, path: str, name: str = None):
        """装饰器：添加POST路由"""
        return self.route(path, ['POST'], name)
        
    def put(self, path: str, name: str = None):
        """装饰器：添加PUT路由"""
        return self.route(path, ['PUT'], name)
        
    def delete(self, path: str, name: str = None):
        """装饰器：添加DELETE路由"""
        return self.route(path, ['DELETE'], name)
        
    def match(self, path: str, method: str = 'GET') -> Optional[Route]:
        """匹配路由"""
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
        
    def url_for(self, name: str, **params) -> str:
        """根据路由名称生成URL"""
        for route in self.routes:
            if route.name == name:
                url = route.path
                # 替换URL参数
                for key, value in params.items():
                    url = url.replace('{' + key + '}', str(value))
                return url
                
        raise ValueError(f"No route found with name '{name}'")
        
    def group(self, prefix: str):
        """创建路由组"""
        group_router = Router()
        
        def add_group_route(path: str, handler: Callable, methods: List[str], name: str = None):
            full_path = prefix + path
            self.add(full_path, handler, methods, name)
            
        group_router.add = add_group_route
        return group_router
        
    def mount(self, prefix: str, router: 'Router'):
        """挂载其他路由器"""
        for route in router.routes:
            full_path = prefix + route.path
            self.add(full_path, route.handler, route.methods, route.name)
        return self
        
    def middleware(self, middleware_func: Callable):
        """添加路由中间件"""
        original_routes = self.routes[:]
        for route in original_routes:
            original_handler = route.handler
            
            def wrapped_handler(*args, **kwargs):
                return middleware_func(original_handler, *args, **kwargs)
                
            route.handler = wrapped_handler
        return self
