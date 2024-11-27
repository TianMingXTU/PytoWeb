"""
Performance optimizations for PytoWeb components
"""

from typing import Dict, Any, List, Optional, Callable
from functools import lru_cache, wraps
import time
import logging

class VirtualScroll:
    """Virtual scrolling implementation for large lists"""
    
    def __init__(self, items: List[Any], item_height: int = 40, 
                 container_height: int = 400, buffer_size: int = 5):
        self.items = items
        self.item_height = item_height
        self.container_height = container_height
        self.buffer_size = buffer_size
        self.scroll_top = 0
        
    def get_visible_items(self, scroll_top: int) -> List[Any]:
        """Get only the items that should be visible"""
        self.scroll_top = scroll_top
        
        # Calculate visible range
        start_index = max(0, scroll_top // self.item_height - self.buffer_size)
        visible_count = self.container_height // self.item_height + 2 * self.buffer_size
        end_index = min(len(self.items), start_index + visible_count)
        
        return self.items[start_index:end_index]
        
    def get_padding_top(self) -> int:
        """Get padding top to maintain scroll position"""
        return max(0, self.scroll_top // self.item_height - self.buffer_size) * self.item_height
        
    def get_padding_bottom(self) -> int:
        """Get padding bottom to maintain scroll height"""
        visible_count = self.container_height // self.item_height + 2 * self.buffer_size
        return max(0, (len(self.items) - (self.scroll_top // self.item_height + visible_count))) * self.item_height


class Debounce:
    """防抖装饰器类，用于限制函数调用频率。
    
    该类实现了一个防抖机制，确保函数在指定时间内只被调用一次。
    
    Args:
        wait_ms: 等待时间（毫秒）
    """
    
    def __init__(self, wait_ms: int = 300):
        """初始化防抖装饰器。
        
        Args:
            wait_ms: 等待时间（毫秒），默认为300ms
        """
        self.wait_ms = wait_ms
        self.last_call = 0
        self._logger = logging.getLogger(__name__)

    def __call__(self, func: Callable) -> Callable:
        """调用装饰器。
        
        Args:
            func: 要装饰的函数
            
        Returns:
            装饰后的函数
        """
        @wraps(func)
        def wrapped(*args, **kwargs):
            current_time = time.time() * 1000
            if current_time - self.last_call >= self.wait_ms:
                self.last_call = current_time
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    self._logger.error(f"Error in debounced function {func.__name__}: {e}", exc_info=True)
                    raise
        return wrapped


@lru_cache(maxsize=100)
def cache_render(component: Any, props: frozenset) -> str:
    """Cache component render results"""
    return component.render()


class LazyLoad:
    """Lazy loading implementation for components"""
    
    def __init__(self, factory: Callable[[], Any]):
        self.factory = factory
        self._instance = None
        
    def get_instance(self) -> Any:
        """Get or create component instance"""
        if self._instance is None:
            self._instance = self.factory()
        return self._instance


class StateManager:
    """Efficient state management with change detection"""
    
    def __init__(self):
        self._state: Dict[str, Any] = {}
        self._listeners: Dict[str, List[Callable]] = {}
        self._batch_updates = False
        self._pending_updates: Dict[str, Any] = {}
        
    def get(self, key: str) -> Any:
        """Get state value"""
        return self._state.get(key)
        
    def set(self, key: str, value: Any):
        """Set state value with change detection"""
        if self._batch_updates:
            self._pending_updates[key] = value
            return
            
        if key not in self._state or self._state[key] != value:
            self._state[key] = value
            self._notify_listeners(key)
            
    def batch_update(self):
        """Start batch update"""
        self._batch_updates = True
        
    def commit(self):
        """Commit batch update"""
        self._batch_updates = False
        changed_keys = set()
        
        for key, value in self._pending_updates.items():
            if key not in self._state or self._state[key] != value:
                self._state[key] = value
                changed_keys.add(key)
                
        self._pending_updates.clear()
        
        # Notify listeners only once per key
        for key in changed_keys:
            self._notify_listeners(key)
            
    def subscribe(self, key: str, listener: Callable):
        """Subscribe to state changes"""
        if key not in self._listeners:
            self._listeners[key] = []
        self._listeners[key].append(listener)
        
    def _notify_listeners(self, key: str):
        """Notify state change listeners"""
        if key in self._listeners:
            value = self._state[key]
            for listener in self._listeners[key]:
                listener(value)
