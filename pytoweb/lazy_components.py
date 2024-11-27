"""Lazy loading components including image lazy loading and infinite scroll"""
from typing import List, Dict, Any, Optional, Callable, Union
from .components import Component, Image
from .events import EventDelegate
import time

class LazyImage(Component):
    """Image component with lazy loading capability"""
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
        
        # 设置初始样式
        self.style.add(
            opacity="0",
            transition="opacity 0.3s ease-in-out"
        )
        
        # 初始化Intersection Observer
        self._init_observer()
        
    def _default_placeholder(self) -> str:
        """Generate default placeholder image"""
        return "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Crect width='24' height='24' fill='%23f0f0f0'/%3E%3C/svg%3E"
        
    def _init_observer(self):
        """Initialize intersection observer"""
        self.set_prop('_observer', {
            'root': None,
            'rootMargin': '50px',
            'threshold': self.props['threshold']
        })
        
        def callback(entries, observer):
            for entry in entries:
                if entry.isIntersecting:
                    self._load_image()
                    observer.unobserve(entry.target)
                    
        self.set_prop('_observer_callback', callback)
        
    def _load_image(self):
        """Load the actual image"""
        if not self.state['loaded']:
            img = Image(self.props['data-src'])
            img.on_load.add(self._handle_load)
            img.on_error.add(self._handle_error)
            
    def _handle_load(self, event: Dict[str, Any]):
        """Handle image load success"""
        self.set_state('loaded', True)
        self.style.add(opacity="1")
        
    def _handle_error(self, event: Dict[str, Any]):
        """Handle image load error"""
        self.set_state('error', True)
        self.set_prop('src', self.props['placeholder'])
        self.style.add(opacity="1")
        
    def render(self):
        """Render lazy image"""
        return super().render()

class InfiniteScroll(Component):
    """Infinite scrolling container component"""
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
        
        # 设置容器样式
        self.style.add(
            overflow_y="auto",
            height="100%"
        )
        
        # 初始化滚动监听
        self.on_scroll = EventDelegate()
        self.on_scroll.add(self._handle_scroll)
        
        # 初始加载
        self._load_items()
        
    def _default_loading(self) -> Component:
        """Default loading component"""
        loading = Component()
        loading.tag_name = "div"
        loading.style.add(
            text_align="center",
            padding="1rem"
        )
        loading.set_text("Loading...")
        return loading
        
    async def _load_items(self):
        """Load more items"""
        if not self.state['loading'] and self.state['has_more']:
            try:
                self.set_state('loading', True)
                self.set_state('error', None)
                
                new_items = await self.props['load_more']()
                if not new_items or len(new_items) == 0:
                    self.set_state('has_more', False)
                else:
                    current_items = self.state['items']
                    self.set_state('items', current_items + new_items)
                    
            except Exception as e:
                self.set_state('error', str(e))
            finally:
                self.set_state('loading', False)
                
    def _handle_scroll(self, event: Dict[str, Any]):
        """Handle scroll events"""
        target = event.get('target', {})
        scroll_top = target.get('scrollTop', 0)
        scroll_height = target.get('scrollHeight', 0)
        client_height = target.get('clientHeight', 0)
        
        # 检查是否接近底部
        if (scroll_height - scroll_top - client_height) < self.props['threshold']:
            self._load_items()
            
    def render(self):
        """Render infinite scroll container"""
        container = Component()
        container.tag_name = "div"
        
        # 渲染项目列表
        for item in self.state['items']:
            container.add_child(self.props['render_item'](item))
            
        # 渲染加载状态
        if self.state['loading']:
            container.add_child(self.props['loading_component'])
            
        # 渲染错误状态
        if self.state['error']:
            error_component = Component()
            error_component.tag_name = "div"
            error_component.style.add(
                color="red",
                text_align="center",
                padding="1rem"
            )
            error_component.set_text(f"Error: {self.state['error']}")
            container.add_child(error_component)
            
        return container
