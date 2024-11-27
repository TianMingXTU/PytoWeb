"""
延迟加载系统，包括组件、图片和无限滚动的延迟加载功能。
"""

from typing import Dict, Any, List, Optional, Callable, Union
from collections import OrderedDict
import importlib
import inspect
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from .components import Component, Image
from .events import EventDelegate

class ComponentLoadError(Exception):
    """组件加载错误"""
    pass

class ResourceMetadata:
    """资源元数据"""
    def __init__(self,
                 path: str,
                 type: str,
                 size: int,
                 priority: int = 0,
                 dependencies: List[str] = None):
        self.path = path
        self.type = type
        self.size = size
        self.priority = priority
        self.dependencies = dependencies or []

class LRUCache:
    """LRU缓存实现"""
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()
        
    def get(self, key: str) -> Any:
        if key not in self.cache:
            return None
        self.cache.move_to_end(key)
        return self.cache[key]
        
    def set(self, key: str, value: Any):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

class LazyComponentLoader:
    """延迟加载组件的加载器类。
    
    该类实现了组件的延迟加载机制，通过缓存和异步加载提高性能。
    
    Args:
        cache_size: 缓存大小，默认为100
    """
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, cache_size: int = 100):
        """初始化加载器。
        
        Args:
            cache_size: 缓存大小
        """
        if not hasattr(self, 'initialized'):
            self._cache = LRUCache(cache_size)
            self._loading: Dict[str, asyncio.Future] = {}
            self._metadata: Dict[str, ResourceMetadata] = {}
            self._executor = ThreadPoolExecutor(max_workers=4)
            self._logger = logging.getLogger(__name__)
            self.initialized = True

        # 确保初始化标志设置正确
        assert self.initialized, "LazyComponentLoader初始化失败"

    async def load_component(self, component_path: str) -> Any:
        """异步加载组件。
        
        Args:
            component_path: 组件路径
            
        Returns:
            加载的组件
            
        Raises:
            ComponentLoadError: 组件加载失败时抛出
        """
        try:
            cached_value = self._cache.get(component_path)
            if cached_value is not None:
                self._logger.debug(f"Component loaded from cache: {component_path}")
                return cached_value
            
            if component_path in self._loading:
                return await self._loading[component_path]
            
            future = asyncio.Future()
            self._loading[component_path] = future
            
            try:
                component = await asyncio.get_event_loop().run_in_executor(
                    self._executor,
                    self._load_component_sync,
                    component_path
                )
                
                self._cache.set(component_path, component)
                self._logger.info(f"Component loaded successfully: {component_path}")
                future.set_result(component)
                return component
                
            except Exception as e:
                self._logger.error(f"Failed to load component {component_path}: {e}", exc_info=True)
                future.set_exception(ComponentLoadError(f"Failed to load component: {e}"))
                raise
            finally:
                del self._loading[component_path]
                
        except Exception as e:
            self._logger.error(f"Unexpected error loading component {component_path}: {e}", exc_info=True)
            raise ComponentLoadError(f"Unexpected error loading component: {e}")

    def _load_component_sync(self, component_path: str) -> Any:
        """同步加载组件。
        
        Args:
            component_path: 组件路径
            
        Returns:
            加载的组件类
        """
        try:
            module_path, class_name = component_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            return getattr(module, class_name)
        except Exception as e:
            raise ComponentLoadError(f"Failed to load component {component_path}: {e}")

    def register_metadata(self, component_path: str, metadata: ResourceMetadata):
        """注册组件元数据。
        
        Args:
            component_path: 组件路径
            metadata: 组件元数据
        """
        self._metadata[component_path] = metadata
        self._logger.debug(f"Registered metadata for: {component_path}")

    def clear_cache(self, component_path: Optional[str] = None):
        """清除缓存。
        
        Args:
            component_path: 要清除的组件路径，如果为None则清除所有缓存
        """
        if component_path:
            self._cache.cache.pop(component_path, None)
            self._logger.debug(f"Cleared cache for: {component_path}")
        else:
            self._cache.cache.clear()
            self._logger.debug("Cleared all cache")

class LazyImage(Component):
    """支持延迟加载的图片组件。
    
    Args:
        src: 图片源URL
        alt: 替代文本
        placeholder: 占位图片URL
        threshold: 可见性阈值
    """
    
    def __init__(self, 
                 src: str,
                 alt: str = "",
                 placeholder: str = "",
                 threshold: float = 0.1):
        super().__init__()
        self.tag_name = "img"
        self.set_prop('data-src', src)
        self.set_prop('alt', alt)
        self.set_prop('threshold', threshold)
        self.set_prop('placeholder', placeholder or self._default_placeholder())
        
        self.state.update({
            'loaded': False,
            'error': False,
            'visible': False
        })
        
        self.style.add(
            opacity="0",
            transition="opacity 0.3s ease-in-out"
        )
        
        self._init_observer()
        self._logger = logging.getLogger(__name__)
        
    def _default_placeholder(self) -> str:
        """生成默认占位图片。"""
        return "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Crect width='24' height='24' fill='%23f0f0f0'/%3E%3C/svg%3E"
        
    def _init_observer(self):
        """初始化交叉观察器。"""
        self.set_prop('_observer', {
            'root': None,
            'rootMargin': '50px',
            'threshold': self.props['threshold']
        })
        
        def callback(entries, observer):
            for entry in entries:
                if entry.isIntersecting:
                    self._load_image()
                    
        self._observer_callback = callback
        
    def _load_image(self):
        """加载图片。"""
        try:
            if not self.state['loaded']:
                self.set_prop('src', self.props['data-src'])
                self.state['loaded'] = True
                self.style.update(opacity="1")
                self._logger.debug(f"Image loaded: {self.props['data-src']}")
        except Exception as e:
            self.state['error'] = True
            self._logger.error(f"Error loading image: {e}", exc_info=True)

class InfiniteScroll(Component):
    """无限滚动容器组件。
    
    Args:
        load_more: 加载更多数据的回调函数
        render_item: 渲染单个项目的回调函数
        threshold: 触发加载的阈值（像素）
        loading_component: 加载中显示的组件
    """
    
    def __init__(self,
                 load_more: Callable[[], List[Any]],
                 render_item: Callable[[Any], Component],
                 threshold: int = 200,
                 loading_component: Optional[Component] = None):
        super().__init__()
        self.tag_name = "div"
        self.set_prop('load_more', load_more)
        self.set_prop('render_item', render_item)
        self.set_prop('threshold', threshold)
        self.set_prop('loading_component', loading_component or self._default_loading())
        
        self.state.update({
            'items': [],
            'loading': False,
            'has_more': True,
            'error': None
        })
        
        self.style.add(
            overflow_y="auto",
            height="100%"
        )
        
        self.on_scroll = EventDelegate()
        self.on_scroll.add(self._handle_scroll)
        
        self._logger = logging.getLogger(__name__)
        self._load_items()
        
    def _default_loading(self) -> Component:
        """默认加载中组件。"""
        loading = Component()
        loading.tag_name = "div"
        loading.style.add(
            text_align="center",
            padding="1rem"
        )
        loading.set_text("Loading...")
        return loading
        
    async def _load_items(self):
        """加载更多项目。"""
        if self.state['loading'] or not self.state['has_more']:
            return
            
        try:
            self.state['loading'] = True
            new_items = await self.props['load_more']()
            
            if not new_items:
                self.state['has_more'] = False
            else:
                self.state['items'].extend(new_items)
                
            self._logger.debug(f"Loaded {len(new_items)} items")
            
        except Exception as e:
            self.state['error'] = str(e)
            self._logger.error(f"Error loading items: {e}", exc_info=True)
            
        finally:
            self.state['loading'] = False
            
    def _handle_scroll(self, event: Dict[str, Any]):
        """处理滚动事件。"""
        try:
            scroll_height = event['target']['scrollHeight']
            scroll_top = event['target']['scrollTop']
            client_height = event['target']['clientHeight']
            
            if scroll_height - (scroll_top + client_height) <= self.props['threshold']:
                asyncio.create_task(self._load_items())
                
        except Exception as e:
            self._logger.error(f"Error handling scroll: {e}", exc_info=True)
            
    def render(self) -> Component:
        """渲染无限滚动容器。"""
        container = Component()
        container.tag_name = "div"
        
        # 渲染项目列表
        for item in self.state['items']:
            try:
                rendered_item = self.props['render_item'](item)
                container.add_child(rendered_item)
            except Exception as e:
                self._logger.error(f"Error rendering item: {e}", exc_info=True)
                
        # 渲染加载状态
        if self.state['loading']:
            container.add_child(self.props['loading_component'])
            
        # 渲染错误状态
        if self.state['error']:
            error_component = Component()
            error_component.tag_name = "div"
            error_component.style.add(
                color="red",
                padding="1rem",
                text_align="center"
            )
            error_component.set_text(f"Error: {self.state['error']}")
            container.add_child(error_component)
            
        return container

def lazy_component(priority: int = 0, dependencies: List[str] = None):
    """延迟加载组件的装饰器。
    
    Args:
        priority: 加载优先级
        dependencies: 依赖的组件列表
    """
    
    def decorator(cls):
        # 获取组件元数据
        metadata = ResourceMetadata(
            path=f"{cls.__module__}.{cls.__name__}",
            type='component',
            size=len(inspect.getsource(cls)),
            priority=priority,
            dependencies=dependencies or []
        )
        
        # 注册元数据
        LazyComponentLoader().register_metadata(metadata.path, metadata)
        
        @functools.wraps(cls)
        async def wrapper(*args, **kwargs):
            # 延迟加载组件
            component_cls = await LazyComponentLoader().load_component(metadata.path)
            return component_cls(*args, **kwargs)
            
        return wrapper
    return decorator

def preload_resources(*paths: str):
    """预加载资源的装饰器。
    
    Args:
        paths: 要预加载的资源路径列表
    """
    
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # 预加载资源
            await ResourcePreloader().preload_resources(list(paths))
            return await func(*args, **kwargs)
        return wrapper
    return decorator

class ResourcePreloader:
    """资源预加载器"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self._preloaded: Dict[str, Any] = {}
            self._priorities: Dict[str, int] = {}
            self._dependencies: Dict[str, List[str]] = {}
            self.initialized = True
        
    def register_resource(self, resource_path: str, priority: int = 0,
                         dependencies: List[str] = None):
        """注册资源。
        
        Args:
            resource_path: 资源路径
            priority: 加载优先级
            dependencies: 依赖的资源列表
        """
        self._priorities[resource_path] = priority
        self._dependencies[resource_path] = dependencies or []
        
    async def preload_resources(self, paths: Optional[List[str]] = None):
        """预加载资源。
        
        Args:
            paths: 要预加载的资源路径列表，如果为None则预加载所有资源
        """
        if paths is None:
            paths = list(self._priorities.keys())
            
        # 按优先级排序
        paths.sort(key=lambda p: self._priorities.get(p, 0), reverse=True)
        
        # 创建预加载任务
        tasks = []
        for path in paths:
            # 加载依赖资源
            for dep in self._dependencies.get(path, []):
                if dep not in self._preloaded:
                    await self.preload_resources([dep])
                    
            if path not in self._preloaded:
                tasks.append(self._preload_resource(path))
                
        await asyncio.gather(*tasks)
        
    async def _preload_resource(self, path: str):
        """预加载单个资源。
        
        Args:
            path: 资源路径
        """
        try:
            if path.endswith('.py'):
                # 预加载Python模块
                module = await asyncio.get_event_loop().run_in_executor(
                    None,
                    importlib.import_module,
                    path
                )
                self._preloaded[path] = module
            else:
                # 其他资源类型预加载逻辑
                pass
                
        except Exception as e:
            logging.error(f"Failed to preload resource {path}: {str(e)}")
            
    def is_preloaded(self, path: str) -> bool:
        """检查资源是否预加载。
        
        Args:
            path: 资源路径
        
        Returns:
            是否预加载
        """
        return path in self._preloaded
        
    def get_preloaded(self, path: str) -> Optional[Any]:
        """获取预加载的资源。
        
        Args:
            path: 资源路径
        
        Returns:
            预加载的资源
        """
        return self._preloaded.get(path)
