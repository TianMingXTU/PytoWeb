"""Asynchronous component rendering and caching system"""
from typing import Dict, Any, Optional, Callable, Union, TypeVar, Generic
from .components import Component
from functools import lru_cache
import asyncio
import time
import weakref

T = TypeVar('T')

class ComponentCache:
    """LRU cache for component rendering results"""
    def __init__(self, maxsize: int = 128):
        self.maxsize = maxsize
        self._cache: Dict[str, tuple[Any, float]] = {}
        self._access_times: Dict[str, float] = {}
        
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        if key in self._cache:
            value, expire_time = self._cache[key]
            if expire_time > time.time():
                self._access_times[key] = time.time()
                return value
            else:
                del self._cache[key]
                del self._access_times[key]
        return None
        
    def set(self, key: str, value: Any, ttl: int = 300):
        """Set item in cache with TTL"""
        if len(self._cache) >= self.maxsize:
            # 移除最少访问的项
            oldest_key = min(self._access_times.items(), key=lambda x: x[1])[0]
            del self._cache[oldest_key]
            del self._access_times[oldest_key]
            
        expire_time = time.time() + ttl
        self._cache[key] = (value, expire_time)
        self._access_times[key] = time.time()
        
    def clear(self):
        """Clear cache"""
        self._cache.clear()
        self._access_times.clear()

class AsyncComponent(Component):
    """Base class for async components"""
    def __init__(self):
        super().__init__()
        self._cache = ComponentCache()
        self._pending_renders = weakref.WeakSet()
        
    async def render_async(self) -> Component:
        """Asynchronous render method"""
        raise NotImplementedError
        
    def _get_cache_key(self) -> str:
        """Generate cache key based on props and state"""
        return f"{self.__class__.__name__}:{hash(str(self.props))}:{hash(str(self.state))}"
        
    async def get_rendered_component(self) -> Component:
        """Get rendered component with caching"""
        cache_key = self._get_cache_key()
        cached = self._cache.get(cache_key)
        
        if cached is not None:
            return cached
            
        # 创建新的渲染任务
        render_task = asyncio.create_task(self.render_async())
        self._pending_renders.add(render_task)
        
        try:
            result = await render_task
            self._cache.set(cache_key, result)
            return result
        finally:
            self._pending_renders.remove(render_task)

class AsyncRenderer:
    """Asynchronous component renderer"""
    def __init__(self, concurrency: int = 10):
        self.concurrency = concurrency
        self._semaphore = asyncio.Semaphore(concurrency)
        self._cache = ComponentCache()
        
    async def render_component(self, component: AsyncComponent) -> Component:
        """Render component with concurrency control"""
        async with self._semaphore:
            return await component.get_rendered_component()
            
    async def render_many(self, components: list[AsyncComponent]) -> list[Component]:
        """Render multiple components concurrently"""
        tasks = [self.render_component(comp) for comp in components]
        return await asyncio.gather(*tasks)

class Suspense(AsyncComponent):
    """Component for handling async loading states"""
    def __init__(self,
                 component: AsyncComponent,
                 fallback: Optional[Component] = None,
                 error_fallback: Optional[Component] = None):
        super().__init__()
        self.set_prop('component', component)
        self.set_prop('fallback', fallback or self._default_fallback())
        self.set_prop('error_fallback', error_fallback or self._default_error())
        
        self.state.update({
            'loading': True,
            'error': None
        })
        
    def _default_fallback(self) -> Component:
        """Default loading component"""
        loading = Component()
        loading.tag_name = "div"
        loading.style.add(
            text_align="center",
            padding="1rem"
        )
        loading.set_text("Loading...")
        return loading
        
    def _default_error(self) -> Component:
        """Default error component"""
        error = Component()
        error.tag_name = "div"
        error.style.add(
            color="red",
            text_align="center",
            padding="1rem"
        )
        error.set_text("Error loading component")
        return error
        
    async def render_async(self) -> Component:
        """Render async component with suspense"""
        try:
            self.set_state('loading', True)
            result = await self.props['component'].get_rendered_component()
            self.set_state('loading', False)
            return result
        except Exception as e:
            self.set_state('loading', False)
            self.set_state('error', str(e))
            return self.props['error_fallback']
            
    def render(self) -> Component:
        """Synchronous render method"""
        if self.state['loading']:
            return self.props['fallback']
        elif self.state['error']:
            return self.props['error_fallback']
        return super().render()

class ErrorBoundary(Component):
    """Component for handling errors in child components"""
    def __init__(self,
                 children: list[Component],
                 fallback: Optional[Callable[[Exception], Component]] = None):
        super().__init__()
        self.set_prop('children', children)
        self.set_prop('fallback', fallback or self._default_fallback)
        
        self.state.update({
            'error': None,
            'error_info': None
        })
        
    def _default_fallback(self, error: Exception) -> Component:
        """Default error fallback"""
        error_component = Component()
        error_component.tag_name = "div"
        error_component.style.add(
            color="red",
            padding="1rem",
            border="1px solid red",
            margin="1rem"
        )
        error_component.set_text(f"Error: {str(error)}")
        return error_component
        
    def render(self) -> Component:
        """Render with error handling"""
        if self.state['error']:
            return self.props['fallback'](self.state['error'])
            
        container = Component()
        container.tag_name = "div"
        
        try:
            for child in self.props['children']:
                container.add_child(child)
        except Exception as e:
            self.set_state('error', e)
            return self.props['fallback'](e)
            
        return container
