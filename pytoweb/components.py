"""
PytoWeb组件系统

提供基础和高级UI组件，支持虚拟滚动、拖放等功能。
"""

from __future__ import annotations
from typing import (
    Dict, Any, Optional, Callable, List, Set,
    TypeVar, TypedDict, Union, TYPE_CHECKING
)
from collections import OrderedDict
import weakref
import logging
from .elements import Element
from .styles import Style
from .events import EventDelegate, Event
import time
import sys
import asyncio
import uuid
import traceback
from dataclasses import dataclass
from datetime import datetime
import json
from functools import wraps

if TYPE_CHECKING:
    from typing import Literal

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 类型别名
T = TypeVar('T')
OptionsType = List[Dict[str, str]]
EventHandler = Callable[..., None]
ComponentList = List['Component']
PropDict = Dict[str, Any]
StateDict = Dict[str, Any]

class ComponentCache:
    """组件缓存系统"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
        
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self._cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()
            self._max_size = 100  # 最大缓存项数
            self._max_memory = 100 * 1024 * 1024  # 最大内存使用(100MB)
            self._ttl = 300  # 缓存过期时间(秒)
            self._current_memory = 0
            self._logger = logging.getLogger(__name__)
            self.initialized = True
            
    def get(self, key: str) -> Optional[Any]:
        """获取缓存的组件"""
        try:
            if key in self._cache:
                value, timestamp = self._cache[key]
                current_time = time.time()
                
                # 检查是否过期
                if current_time - timestamp > self._ttl:
                    self._cache.pop(key)
                    self._current_memory -= sys.getsizeof(value)
                    return None
                    
                # 更新访问顺序和时间戳
                self._cache.move_to_end(key)
                self._cache[key] = (value, current_time)
                return value
        except Exception as e:
            self._logger.error(f"Error getting cached component: {e}", exc_info=True)
        return None
        
    def set(self, key: str, value: Any):
        """缓存组件"""
        try:
            current_time = time.time()
            value_size = sys.getsizeof(value)
            
            # 检查单个值是否超过最大内存限制
            if value_size > self._max_memory:
                self._logger.warning(f"Value too large to cache: {value_size} bytes")
                return
                
            # 如果已存在，先移除旧值
            if key in self._cache:
                old_value, _ = self._cache.pop(key)
                self._current_memory -= sys.getsizeof(old_value)
                
            # 清理过期和超出内存限制的缓存
            while self._cache and (
                len(self._cache) >= self._max_size or
                self._current_memory + value_size > self._max_memory or
                current_time - next(iter(self._cache.values()))[1] > self._ttl
            ):
                removed_key = next(iter(self._cache))
                removed_value, _ = self._cache.pop(removed_key)
                self._current_memory -= sys.getsizeof(removed_value)
                
            # 添加新值
            self._cache[key] = (value, current_time)
            self._current_memory += value_size
            
        except Exception as e:
            self._logger.error(f"Error caching component: {e}", exc_info=True)
            
    def clear(self):
        """清除缓存"""
        self._cache.clear()
        self._current_memory = 0
        
    def get_stats(self) -> dict:
        """获取缓存统计信息"""
        return {
            'size': len(self._cache),
            'memory_usage': self._current_memory,
            'max_size': self._max_size,
            'max_memory': self._max_memory,
            'ttl': self._ttl
        }

class Component:
    """所有组件的基类"""
    
    def __init__(self):
        self.props: PropDict = {}
        self.state: StateDict = {}
        self.children: ComponentList = []
        self.parent: Optional['Component'] = None
        self.style = Style()
        self.tag_name = "div"  # 默认标签
        self._cache = ComponentCache()
        self._logger = logging.getLogger(__name__)
        self._mounted = False
        self._destroyed = False
        
        # 生命周期事件
        self.on_before_mount = EventDelegate()
        self.on_mounted = EventDelegate()
        self.on_before_update = EventDelegate()
        self.on_updated = EventDelegate()
        self.on_before_destroy = EventDelegate()
        self.on_destroyed = EventDelegate()
        self.on_error = EventDelegate()
        
        # 状态变更事件
        self.on_state_change = EventDelegate()
        self.on_prop_change = EventDelegate()
        
        self._memo_cache = {}
        self._memo_deps = {}
        
        self._lazy_loaded = False
        self._lazy_loading = False
        self._lazy_error = None
        self._lazy_promise = None
        
    def set_prop(self, key: str, value: Any):
        """设置属性"""
        try:
            old_value = self.props.get(key)
            if old_value != value:
                self.props[key] = value
                self.on_prop_change(self, key, old_value, value)
                self._update()
        except Exception as e:
            self._logger.error(f"Error setting prop {key}: {e}", exc_info=True)
            self.on_error(self, e)
            
    def set_state(self, key: str, value: Any):
        """设置状态"""
        try:
            old_value = self.state.get(key)
            if old_value != value:
                self.state[key] = value
                self.on_state_change(self, key, old_value, value)
                self._update()
        except Exception as e:
            self._logger.error(f"Error setting state {key}: {e}", exc_info=True)
            self.on_error(self, e)
            
    def add_child(self, child: 'Component'):
        """添加子组件"""
        try:
            child.parent = self
            self.children.append(child)
            self._update()
        except Exception as e:
            self._logger.error(f"Error adding child: {e}", exc_info=True)
            self.on_error(self, e)
            
    def remove_child(self, child: 'Component'):
        """移除子组件"""
        try:
            if child in self.children:
                child.parent = None
                self.children.remove(child)
                self._update()
        except Exception as e:
            self._logger.error(f"Error removing child: {e}", exc_info=True)
            self.on_error(self, e)
            
    def mount(self):
        """组件挂载"""
        try:
            if not self._mounted:
                self.on_before_mount(self)
                self._mounted = True
                for child in self.children:
                    child.mount()
                self.on_mounted(self)
        except Exception as e:
            self._logger.error(f"Error mounting component: {e}", exc_info=True)
            self.on_error(self, e)
            
    def unmount(self):
        """组件卸载"""
        try:
            if self._mounted and not self._destroyed:
                self.on_before_destroy(self)
                self._mounted = False
                self._destroyed = True
                for child in self.children:
                    child.unmount()
                self.on_destroyed(self)
        except Exception as e:
            self._logger.error(f"Error unmounting component: {e}", exc_info=True)
            self.on_error(self, e)
            
    def _update(self):
        """更新组件"""
        try:
            if self._mounted and not self._destroyed:
                self.on_before_update(self)
                # 实际更新逻辑
                self.on_updated(self)
        except Exception as e:
            self._logger.error(f"Error updating component: {e}", exc_info=True)
            self.on_error(self, e)
            
    def validate_props(self, prop_types: Dict[str, type]):
        """验证属性类型"""
        for key, expected_type in prop_types.items():
            if key in self.props:
                value = self.props[key]
                if not isinstance(value, expected_type):
                    raise TypeError(f"Prop '{key}' expected type {expected_type.__name__}, got {type(value).__name__}")
                    
    def validate_state(self, state_types: Dict[str, type]):
        """验证状态类型"""
        for key, expected_type in state_types.items():
            if key in self.state:
                value = self.state[key]
                if not isinstance(value, expected_type):
                    raise TypeError(f"State '{key}' expected type {expected_type.__name__}, got {type(value).__name__}")
                    
    def render(self):
        """渲染组件"""
        try:
            print(f"[DEBUG] Rendering component: {self.__class__.__name__}")
            element = Element(self.tag_name)
            
            # 添加样式
            if self.style:
                element.style.update(self.style.get_all())
                print(f"[DEBUG] Added styles: {self.style.get_all()}")
            
            # 添加子组件
            for child in self.children:
                try:
                    child_element = child.render()
                    if child_element:
                        element.add(child_element)
                        print(f"[DEBUG] Added child element: {child.__class__.__name__}")
                    else:
                        print(f"[WARNING] Child {child.__class__.__name__} rendered None")
                except Exception as e:
                    print(f"[ERROR] Failed to render child {child.__class__.__name__}: {e}")
                    raise
            
            return element
        except Exception as e:
            print(f"[ERROR] Failed to render {self.__class__.__name__}: {e}")
            raise
            
    def memo(self, key: str, fn: Callable[..., Any], *deps: Any) -> Any:
        """记忆化计算结果
        
        Args:
            key: 缓存键名
            fn: 要记忆化的函数
            deps: 依赖项，当这些值变化时重新计算
            
        Returns:
            记忆化的计算结果
        """
        current_deps = tuple(deps)
        
        # 检查依赖是否变化
        if (key not in self._memo_cache or
            key not in self._memo_deps or
            self._memo_deps[key] != current_deps):
            
            # 重新计算并缓存结果
            self._memo_cache[key] = fn()
            self._memo_deps[key] = current_deps
            
        return self._memo_cache[key]
        
    def clear_memo(self, key: Optional[str] = None):
        """清除记忆化缓存
        
        Args:
            key: 要清除的特定缓存键,如果为None则清除所有缓存
        """
        if key is None:
            self._memo_cache.clear()
            self._memo_deps.clear()
        else:
            self._memo_cache.pop(key, None)
            self._memo_deps.pop(key, None)

    def lazy_load(self, loader: Callable[[], Awaitable[Any]]) -> None:
        """懒加载组件内容
        
        Args:
            loader: 异步加载函数
        """
        if not self._lazy_loaded and not self._lazy_loading:
            self._lazy_loading = True
            self._lazy_promise = asyncio.create_task(self._do_lazy_load(loader))
            
    async def _do_lazy_load(self, loader: Callable[[], Awaitable[Any]]) -> None:
        """执行懒加载
        
        Args:
            loader: 异步加载函数
        """
        try:
            result = await loader()
            self._handle_lazy_load_success(result)
        except Exception as e:
            self._handle_lazy_load_error(e)
            
    def _handle_lazy_load_success(self, result: Any) -> None:
        """处理懒加载成功
        
        Args:
            result: 加载结果
        """
        self._lazy_loaded = True
        self._lazy_loading = False
        self._lazy_error = None
        self.state['lazy_result'] = result
        self._update()
        
    def _handle_lazy_load_error(self, error: Exception) -> None:
        """处理懒加载错误
        
        Args:
            error: 错误信息
        """
        self._lazy_loaded = False
        self._lazy_loading = False
        self._lazy_error = error
        self._update()
        
    def is_lazy_loaded(self) -> bool:
        """检查是否已完成懒加载"""
        return self._lazy_loaded
        
    def is_lazy_loading(self) -> bool:
        """检查是否正在懒加载"""
        return self._lazy_loading
        
    def get_lazy_error(self) -> Optional[Exception]:
        """获取懒加载错误信息"""
        return self._lazy_error

class AsyncComponentMixin:
    """为组件添加异步支持的Mixin类"""
    def __init__(self):
        super().__init__()
        self._cache = ComponentCache()
        self._pending_updates = {}
        
    async def update_async(self, **kwargs):
        """异步更新组件状态"""
        update_id = str(uuid.uuid4())
        self._pending_updates[update_id] = asyncio.Future()
        
        try:
            await self.on_before_update.emit_async()
            self.state.update(kwargs)
            await self.on_updated.emit_async()
            self._pending_updates[update_id].set_result(True)
        except Exception as e:
            self._pending_updates[update_id].set_exception(e)
        finally:
            del self._pending_updates[update_id]
            
    async def render_async(self):
        """异步渲染组件"""
        cache_key = self._get_cache_key()
        cached = self._cache.get(cache_key)
        if cached:
            return cached
            
        try:
            await self.on_before_mount.emit_async()
            result = await self._render_async_impl()
            await self.on_mounted.emit_async()
            
            self._cache.set(cache_key, result)
            return result
        except Exception as e:
            self.logger.error(f"Error in async rendering: {e}")
            raise
            
    async def _render_async_impl(self):
        """异步渲染实现"""
        raise NotImplementedError("Async components must implement _render_async_impl")

class AsyncComponent(AsyncComponentMixin, Component):
    """异步组件基类"""
    pass

class Suspense(Component):
    """处理异步加载状态的组件"""
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
        
    def _default_fallback(self):
        """默认加载组件"""
        loading = Component()
        loading.tag_name = "div"
        loading.style.add(
            text_align="center",
            padding="1rem"
        )
        loading.set_text("Loading...")
        return loading
        
    def _default_error(self):
        """默认错误组件"""
        error = Component()
        error.tag_name = "div"
        error.style.add(
            color="red",
            text_align="center",
            padding="1rem"
        )
        error.set_text("An error occurred")
        return error
        
    async def render_async(self):
        """异步渲染"""
        try:
            if self.state['loading']:
                return self.props['fallback']
                
            result = await self.props['component'].render_async()
            self.state['loading'] = False
            return result
        except Exception as e:
            self.state['error'] = str(e)
            self.logger.error(f"Error in Suspense: {e}")
            return self.props['error_fallback']

class ErrorBoundary(Component):
    """错误边界组件，用于捕获和处理子组件中的错误"""
    
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
        
        self._error_handler = ErrorHandler.get_instance()
        
    def _default_fallback(self, error: Exception) -> Component:
        """默认错误回退组件"""
        error_component = Component()
        error_component.tag_name = "div"
        error_component.style.add(
            color="red",
            padding="1rem",
            border="1px solid red",
            margin="1rem",
            background_color="rgba(255,0,0,0.1)"
        )
        error_component.set_text(f"Error: {str(error)}")
        return error_component
        
    def render(self):
        """渲染错误边界"""
        if self.state['error']:
            error_component = self.props['fallback'](self.state['error'])
            return error_component
            
        try:
            return self.props['children']
        except Exception as e:
            self.state['error'] = e
            self.state['error_info'] = self._error_handler._get_error_context()
            self._error_handler.handle_error(e, self.state['error_info'])
            return self.props['fallback'](e)

@dataclass
class ErrorContext:
    """错误上下文信息"""
    component: Optional[str] = None
    function: Optional[str] = None
    line_number: Optional[int] = None
    file_path: Optional[str] = None
    stack_trace: Optional[str] = None
    additional_info: Dict[str, Any] = None

@dataclass
class ErrorReport:
    """详细错误报告"""
    error_type: str
    message: str
    context: ErrorContext
    timestamp: datetime
    severity: str
    handled: bool

class ErrorHandler:
    """中央错误处理系统"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
        
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.error_listeners: List[Callable[[ErrorReport], None]] = []
            self.error_history: List[ErrorReport] = []
            self.max_history = 100
            self.logger = logging.getLogger('pytoweb.errors')
            self.initialized = True
            
    @classmethod
    def get_instance(cls):
        return cls()
        
    def add_listener(self, listener: Callable[[ErrorReport], None]):
        """添加错误监听器"""
        self.error_listeners.append(listener)
        
    def remove_listener(self, listener: Callable[[ErrorReport], None]):
        """移除错误监听器"""
        self.error_listeners.remove(listener)
        
    def handle_error(self, error: Exception, context: Optional[ErrorContext] = None):
        """处理错误"""
        if context is None:
            context = self._get_error_context()
            
        report = ErrorReport(
            error_type=type(error).__name__,
            message=str(error),
            context=context,
            timestamp=datetime.now(),
            severity=self._get_error_severity(error),
            handled=True
        )
        
        self.error_history.append(report)
        if len(self.error_history) > self.max_history:
            self.error_history.pop(0)
            
        for listener in self.error_listeners:
            try:
                listener(report)
            except Exception as e:
                self.logger.error(f"Error in error listener: {e}")
                
        self.logger.error(f"Error: {report.message}", exc_info=True)
        
    def _get_error_context(self) -> ErrorContext:
        """从当前异常获取上下文"""
        tb = sys.exc_info()[2]
        while tb.tb_next:
            tb = tb.tb_next
            
        frame = tb.tb_frame
        return ErrorContext(
            function=frame.f_code.co_name,
            line_number=tb.tb_lineno,
            file_path=frame.f_code.co_filename,
            stack_trace=traceback.format_exc()
        )
        
    def _get_error_severity(self, error: Exception) -> str:
        """确定错误严重性"""
        if isinstance(error, (SystemError, MemoryError)):
            return "CRITICAL"
        if isinstance(error, (ValueError, TypeError)):
            return "ERROR"
        return "WARNING"
        
    def get_error_summary(self) -> Dict[str, Any]:
        """获取最近错误的摘要"""
        return {
            'total_errors': len(self.error_history),
            'error_types': self._count_error_types(),
            'recent_errors': [
                {
                    'type': e.error_type,
                    'message': e.message,
                    'timestamp': e.timestamp.isoformat()
                }
                for e in self.error_history[-5:]
            ]
        }
        
    def _count_error_types(self) -> Dict[str, int]:
        """统计每种错误类型的出现次数"""
        counts = {}
        for error in self.error_history:
            counts[error.error_type] = counts.get(error.error_type, 0) + 1
        return counts
        
    def export_error_report(self, filepath: str):
        """导出错误历史到文件"""
        try:
            with open(filepath, 'w') as f:
                json.dump(
                    {
                        'error_summary': self.get_error_summary(),
                        'full_history': [
                            {
                                'type': e.error_type,
                                'message': e.message,
                                'timestamp': e.timestamp.isoformat(),
                                'severity': e.severity,
                                'context': {
                                    'component': e.context.component,
                                    'function': e.context.function,
                                    'line': e.context.line_number,
                                    'file': e.context.file_path,
                                    'stack_trace': e.context.stack_trace
                                }
                            }
                            for e in self.error_history
                        ]
                    },
                    f,
                    indent=2
                )
        except Exception as e:
            self.logger.error(f"Failed to export error report: {e}")

def error_boundary(fallback_component: Optional[Callable[[Exception], Component]] = None):
    """错误边界装饰器"""
    def decorator(component_class):
        original_render = component_class.render
        
        @wraps(original_render)
        def wrapped_render(self, *args, **kwargs):
            boundary = ErrorBoundary(
                children=[original_render(self, *args, **kwargs)],
                fallback=fallback_component
            )
            return boundary.render()
            
        component_class.render = wrapped_render
        return component_class
        
    return decorator

class Button(Component):
    """预构建的Button组件"""
    
    def __init__(self, text: str, on_click: Optional[Callable] = None):
        super().__init__()
        self.tag_name = "button"
        self.set_prop('text', text)
        if on_click:
            self.set_prop('on_click', on_click)
        
    def render(self) -> Element:
        button = Element(self.tag_name, text=self.props['text'])
        if 'on_click' in self.props:
            button.on('click', self.props['on_click'])
        return button

class Container(Component):
    """预构建的Container组件"""
    
    def __init__(self, *children: Component):
        super().__init__()
        for child in children:
            self.add_child(child)
        
    def render(self) -> Element:
        container = Element(self.tag_name)
        for child in self.children:
            container.add(child.render())
        return container

class Input(Component):
    """预构建的Input组件"""
    
    def __init__(self, placeholder: str = "", value: str = "", on_change: Optional[Callable] = None):
        super().__init__()
        self.tag_name = "input"
        self.set_prop('placeholder', placeholder)
        self.set_prop('value', value)
        if on_change:
            self.set_prop('on_change', on_change)
        
    def render(self) -> Element:
        input_elem = Element(self.tag_name)
        input_elem.set_attr('placeholder', self.props['placeholder'])
        input_elem.set_attr('value', self.props['value'])
        if 'on_change' in self.props:
            input_elem.on('change', self.props['on_change'])
        return input_elem

class Form(Component):
    """预构建的Form组件"""
    
    def __init__(self, on_submit: Optional[Callable] = None):
        super().__init__()
        self.tag_name = "form"
        if on_submit:
            self.set_prop('on_submit', on_submit)
        
    def render(self) -> Element:
        form = Element(self.tag_name)
        if 'on_submit' in self.props:
            form.on('submit', self.props['on_submit'])
        for child in self.children:
            form.add(child.render())
        return form

class Text(Component):
    """文本组件"""
    
    def __init__(self, text: str, tag: str = "span"):
        super().__init__()
        self.tag_name = tag
        self.set_prop('text', text)
        
    def render(self) -> Element:
        return Element(self.tag_name, text=self.text)

class Image(Component):
    """图像组件"""
    
    def __init__(self, src: str, alt: str = "", width: str = "", height: str = ""):
        super().__init__()
        self.tag_name = "img"
        self.set_prop('src', src)
        self.set_prop('alt', alt)
        if width:
            self.set_prop('width', width)
        if height:
            self.set_prop('height', height)
        
    def render(self) -> Element:
        img = Element(self.tag_name)
        img.set_attr('src', self.src)
        img.set_attr('alt', self.alt)
        if 'width' in self.props:
            img.set_attr('width', self.width)
        if 'height' in self.props:
            img.set_attr('height', self.height)
        return img

class Link(Component):
    """链接组件"""
    
    def __init__(self, href: str, text: str = "", target: str = "_self"):
        super().__init__()
        self.tag_name = "a"
        self.set_prop('href', href)
        self.set_prop('text', text)
        self.set_prop('target', target)
        
    def render(self) -> Element:
        link = Element(self.tag_name, text=self.text)
        link.set_attr('href', self.href)
        link.set_attr('target', self.target)
        return link

class List(Component):
    """列表组件"""
    
    def __init__(self, items: list[str] | None = None, ordered: bool = False):
        super().__init__()
        self.tag_name = "ol" if ordered else "ul"
        self.set_prop('items', items or [])

    def add_item(self, item: str):
        if 'items' not in self.props:
            self.props['items'] = []
        self.props['items'].append(item)
        
    def render(self) -> Element:
        list_elem = Element(self.tag_name)
        for item in self.props.get('items', []):
            li = Element('li', text=str(item))
            list_elem.add(li)
        return list_elem

class Card(Component):
    """卡片组件"""
    
    def __init__(self, title: str = "", body: str = "", footer: str = ""):
        super().__init__()
        self.tag_name = "div"
        self.set_prop('title', title)
        self.set_prop('body', body)
        self.set_prop('footer', footer)
        
    def render(self) -> Element:
        card = Element(self.tag_name)
        card.add_class('card')
        
        if self.title:
            header = Element('div')
            header.add_class('card-header')
            header.add(Element('h3', text=self.title))
            card.add(header)
            
        body = Element('div')
        body.add_class('card-body')
        body.add(Element('p', text=self.body))
        card.add(body)
        
        if self.footer:
            footer = Element('div')
            footer.add_class('card-footer')
            footer.add(Element('p', text=self.footer))
            card.add(footer)
            
        return card

class Grid(Component):
    """网格布局组件"""
    
    def __init__(self, columns: int = 12, gap: str = "1rem"):
        super().__init__()
        self.tag_name = "div"
        self.set_prop('columns', columns)
        self.set_prop('gap', gap)
        self.style.add(
            display="grid",
            grid_template_columns=f"repeat({columns}, 1fr)",
            gap=gap
        )
        
    def add_item(self, component: Component, column_span: int = 1):
        component.style.add(grid_column=f"span {column_span}")
        self.add_child(component)
        
    def render(self) -> Element:
        grid = Element(self.tag_name)
        for child in self.children:
            grid.add(child.render())
        return grid

class Select(Component):
    """选择组件"""
    
    def __init__(self, options: OptionsType, value: str = "", on_change: Optional[Callable] = None):
        super().__init__()
        self.tag_name = "select"
        self.set_prop('options', options)
        self.set_prop('value', value)
        if on_change:
            self.set_prop('on_change', on_change)
        
    def render(self) -> Element:
        select = Element(self.tag_name)
        if 'on_change' in self.props:
            select.on('change', self.on_change)
            
        for option in self.options:
            opt = Element('option')
            opt.set_attr('value', option.get('value', ''))
            if option.get('value') == self.value:
                opt.set_attr('selected', 'selected')
            opt.text = option.get('label', option.get('value', ''))
            select.add(opt)
            
        return select

class Checkbox(Component):
    """复选框组件"""
    
    def __init__(self, label: str = "", checked: bool = False, on_change: Optional[Callable] = None):
        super().__init__()
        self.tag_name = "input"
        self.set_prop('type', 'checkbox')
        self.set_prop('label', label)
        self.set_prop('checked', checked)
        if on_change:
            self.set_prop('on_change', on_change)
        
    def render(self) -> Element:
        container = Element('div')
        
        input_elem = Element(self.tag_name)
        input_elem.set_attr('type', 'checkbox')
        if self.checked:
            input_elem.set_attr('checked', 'checked')
        if 'on_change' in self.props:
            input_elem.on('change', self.on_change)
        container.add(input_elem)
        
        if self.label:
            label = Element('label')
            label.text = self.label
            container.add(label)
            
        return container

class Radio(Component):
    """单选框组件"""
    
    def __init__(self, name: str, value: str, label: str = "", checked: bool = False, on_change: Optional[Callable] = None):
        super().__init__()
        self.tag_name = "input"
        self.set_prop('type', 'radio')
        self.set_prop('name', name)
        self.set_prop('value', value)
        self.set_prop('label', label)
        self.set_prop('checked', checked)
        if on_change:
            self.set_prop('on_change', on_change)
        
    def render(self) -> Element:
        container = Element('div')
        
        input_elem = Element(self.tag_name)
        input_elem.set_attr('type', 'radio')
        input_elem.set_attr('name', self.name)
        input_elem.set_attr('value', self.value)
        if self.checked:
            input_elem.set_attr('checked', 'checked')
        if 'on_change' in self.props:
            input_elem.on('change', self.on_change)
        container.add(input_elem)
        
        if self.label:
            label = Element('label')
            label.text = self.label
            container.add(label)
            
        return container

class TextArea(Component):
    """文本域组件"""
    
    def __init__(self, value: str = "", placeholder: str = "", rows: int = 3, on_change: Optional[Callable] = None):
        super().__init__()
        self.tag_name = "textarea"
        self.set_prop('value', value)
        self.set_prop('placeholder', placeholder)
        self.set_prop('rows', rows)
        if on_change:
            self.set_prop('on_change', on_change)
        
    def render(self) -> Element:
        textarea = Element(self.tag_name, text=self.value)
        textarea.set_attr('placeholder', self.placeholder)
        textarea.set_attr('rows', str(self.rows))
        if 'on_change' in self.props:
            textarea.on('change', self.on_change)
        return textarea

class Navbar(Component):
    """导航栏组件"""
    
    def __init__(self, brand: str = "", items: list[dict[str, str]] = None, theme: str = "light"):
        super().__init__()
        self.tag_name = "nav"
        self.set_prop('brand', brand)
        self.set_prop('items', items or [])
        self.set_prop('theme', theme)
        self.style.add(
            display="flex",
            align_items="center",
            padding="1rem",
            background_color="#ffffff" if theme == "light" else "#343a40",
            color="#000000" if theme == "light" else "#ffffff"
        )
        
    def add_item(self, text: str, href: str = "#", active: bool = False):
        self.props['items'].append({
            'text': text,
            'href': href,
            'active': active
        })
        
    def render(self) -> Element:
        nav = Element(self.tag_name)
        
        if self.brand:
            brand = Element('a')
            brand.add_class('navbar-brand')
            brand.set_attr('href', '#')
            brand.text = self.brand
            brand.style.add(
                font_size="1.25rem",
                padding_right="1rem",
                text_decoration="none",
                color="inherit"
            )
            nav.add(brand)
            
        items_container = Element('div')
        items_container.add_class('navbar-items')
        items_container.style.add(
            display="flex",
            gap="1rem"
        )
        
        for item in self.items:
            link = Element('a')
            link.set_attr('href', item.get('href', '#'))
            link.text = item.get('text', '')
            link.style.add(
                text_decoration="none",
                color="inherit"
            )
            if item.get('active'):
                link.style.add(font_weight="bold")
            items_container.add(link)
            
        nav.add(items_container)
        return nav

class Flex(Component):
    """Flexbox容器组件"""
    
    def __init__(self, direction: str = "row", justify: str = "flex-start", align: str = "stretch", wrap: bool = False, gap: str = "0"):
        super().__init__()
        self.tag_name = "div"
        self.style.add(
            display="flex",
            flex_direction=direction,
            justify_content=justify,
            align_items=align,
            flex_wrap="wrap" if wrap else "nowrap",
            gap=gap
        )
        
    def render(self) -> Element:
        flex = Element(self.tag_name)
        for child in self.children:
            flex.add(child.render())
        return flex

class ModernModal(Component):
    """现代模态对话框组件"""
    def __init__(self,
                 title: str,
                 content: str,
                 size: Literal["sm", "md", "lg", "xl"] = "md",
                 centered: bool = True,
                 closable: bool = True):
        super().__init__()
        self.tag_name = "div"
        self.set_prop('title', title)
        self.set_prop('content', content)
        self.set_prop('size', size)
        self.set_prop('centered', centered)
        self.set_prop('closable', closable)
        
        self.state.update({
            'visible': False
        })
        
        # 设置样式
        self.style.add(
            position="fixed",
            top="0",
            left="0",
            width="100%",
            height="100%",
            display="flex",
            align_items="center" if centered else "flex-start",
            justify_content="center",
            background_color="rgba(0, 0, 0, 0.5)",
            z_index="1000",
            opacity="0",
            visibility="hidden",
            transition="opacity 0.3s ease-in-out, visibility 0.3s ease-in-out"
        )
        
    def show(self) -> None:
        """显示模态对话框"""
        self.set_state('visible', True)
        self.style.add(
            opacity="1",
            visibility="visible"
        )
        
    def hide(self) -> None:
        """隐藏模态对话框"""
        self.set_state('visible', False)
        self.style.add(
            opacity="0",
            visibility="hidden"
        )
        
    def _get_size_width(self) -> str:
        """Get modal width based on size"""
        size_map = {
            'sm': '300px',
            'md': '500px',
            'lg': '800px',
            'xl': '1140px'
        }
        return size_map.get(self.props['size'], '500px')
        
    def render(self):
        """渲染模态对话框"""
        dialog = Component()
        dialog.tag_name = "div"
        dialog.style.add(
            background_color="#ffffff",
            border_radius="0.5rem",
            box_shadow="0 25px 50px -12px rgba(0, 0, 0, 0.25)",
            max_width=self._get_size_width(),
            width="100%",
            max_height="90vh",
            display="flex",
            flex_direction="column",
            transform=f"scale({1 if self.state['visible'] else 0.9})",
            transition="transform 0.3s ease-in-out"
        )
        
        # Header
        header = Component()
        header.tag_name = "div"
        header.style.add(
            padding="1rem",
            border_bottom="1px solid #e5e7eb",
            display="flex",
            align_items="center",
            justify_content="space-between"
        )
        
        title = Component()
        title.tag_name = "h3"
        title.style.add(
            margin="0",
            font_size="1.25rem",
            font_weight="600",
            color="#111827"
        )
        title.set_text(self.props['title'])
        header.add_child(title)
        
        if self.props['closable']:
            close_button = Component()
            close_button.tag_name = "button"
            close_button.style.add(
                background="none",
                border="none",
                padding="0.5rem",
                cursor="pointer",
                color="#6b7280"
            )
            close_button.set_text("×")
            close_button.on_click.add(self.hide)
            header.add_child(close_button)
            
        dialog.add_child(header)
        
        # Content
        content = Component()
        content.tag_name = "div"
        content.style.add(
            padding="1rem",
            overflow_y="auto"
        )
        
        if isinstance(self.props['content'], str):
            content.set_text(self.props['content'])
        else:
            content.add_child(self.props['content'])
            
        dialog.add_child(content)
        
        return dialog

class ModernToast(Component):
    """现代吐司通知组件"""
    
    def __init__(self,
                 message: str,
                 type: str = "info",
                 duration: int = 3000,
                 position: str = "bottom-right"):
        super().__init__()
        self.tag_name = "div"
        self.set_prop('message', message)
        self.set_prop('type', type)
        self.set_prop('duration', duration)
        self.set_prop('position', position)
        
        self.state.update({
            'visible': False
        })
        
        # 设置样式
        self.style.add(
            position="fixed",
            padding="1rem",
            border_radius="0.5rem",
            background_color=self._get_background_color(),
            color="#ffffff",
            box_shadow="0 10px 15px -3px rgba(0, 0, 0, 0.1)",
            max_width="24rem",
            opacity="0",
            transform="translateY(1rem)",
            transition="opacity 0.3s ease-in-out, transform 0.3s ease-in-out",
            **self._get_position_style()
        )
        
    def show(self):
        """显示吐司通知"""
        self.set_state('visible', True)
        self.style.add(
            opacity="1",
            transform="translateY(0)"
        )
        
        # Auto hide
        if self.props['duration'] > 0:
            def hide():
                self.hide()
            setTimeout(hide, self.props['duration'])
            
    def hide(self):
        """隐藏吐司通知"""
        self.set_state('visible', False)
        self.style.add(
            opacity="0",
            transform="translateY(1rem)"
        )
        
    def _get_background_color(self) -> str:
        """Get background color based on type"""
        colors = {
            "info": "#3b82f6",
            "success": "#10b981",
            "warning": "#f59e0b",
            "error": "#ef4444"
        }
        return colors.get(self.props['type'], colors['info'])
        
    def _get_position_style(self) -> dict[str, str]:
        """Get position style"""
        positions = {
            "top-left": {"top": "1rem", "left": "1rem"},
            "top-right": {"top": "1rem", "right": "1rem"},
            "bottom-left": {"bottom": "1rem", "left": "1rem"},
            "bottom-right": {"bottom": "1rem", "right": "1rem"}
        }
        return positions.get(self.props['position'], positions['bottom-right'])
        
    def render(self):
        """Render toast"""
        container = Component()
        container.tag_name = "div"
        container.style.add(
            display="flex",
            align_items="center",
            gap="0.5rem"
        )
        
        # Icon
        icon = Component()
        icon.tag_name = "span"
        icon.style.add(
            font_size="1.25rem"
        )
        icon.set_text(self._get_icon())
        container.add_child(icon)
        
        # Message
        message = Component()
        message.tag_name = "span"
        message.set_text(self.props['message'])
        container.add_child(message)
        
        return container
        
    def _get_icon(self) -> str:
        """Get icon based on type"""
        icons = {
            "info": "ℹ",
            "success": "✓",
            "warning": "⚠",
            "error": "✕"
        }
        return icons.get(self.props['type'], icons['info'])

class ModernTabs(Component):
    """现代选项卡组件"""
    
    def __init__(self,
                 tabs: list[dict[str, Any]],
                 active_index: int = 0,
                 variant: str = "default"):
        super().__init__()
        self.tag_name = "div"
        self.set_prop('tabs', tabs)
        self.set_prop('variant', variant)
        
        self.state.update({
            'active_index': active_index
        })

    def _handle_tab_click(self, index: int):
        """Handle tab click"""
        self.set_state('active_index', index)
        
    def render(self):
        """Render tabs"""
        container = Component()
        container.tag_name = "div"
        
        # Tab list
        tab_list = Component()
        tab_list.tag_name = "div"
        tab_list.style.add(
            display="flex",
            border_bottom="1px solid #e5e7eb"
        )
        
        for i, tab in enumerate(self.props['tabs']):
            tab_button = Component()
            tab_button.tag_name = "button"
            tab_button.style.add(
                padding="0.75rem 1rem",
                border="none",
                background="none",
                font_weight="500",
                color="#6b7280" if i != self.state['active_index'] else "#111827",
                border_bottom=f"2px solid {'transparent' if i != self.state['active_index'] else '#3b82f6'}",
                cursor="pointer",
                transition="all 0.2s ease-in-out"
            )
            tab_button.set_text(tab['label'])
            tab_button.on_click.add(lambda e, i=i: self._handle_tab_click(i))
            tab_list.add_child(tab_button)
            
        container.add_child(tab_list)
        
        # Tab panels
        panel_container = Component()
        panel_container.tag_name = "div"
        panel_container.style.add(
            padding="1rem"
        )
        
        active_tab = self.props['tabs'][self.state['active_index']]
        if isinstance(active_tab['content'], str):
            panel_container.set_text(active_tab['content'])
        else:
            panel_container.add_child(active_tab['content'])
            
        container.add_child(panel_container)
        
        return container

class ModernAccordion(Component):
    """现代手风琴组件"""
    
    def __init__(self,
                 items: list[dict[str, Any]],
                 multiple: bool = False):
        super().__init__()
        self.tag_name = "div"
        self.set_prop('items', items)
        self.set_prop('multiple', multiple)
        
        self.state.update({
            'expanded': set()
        })

    def _toggle_item(self, index: int):
        """Toggle accordion item"""
        expanded = self.state['expanded'].copy()
        
        if not self.props['multiple']:
            expanded.clear()
            
        if index in expanded:
            expanded.remove(index)
        else:
            expanded.add(index)
            
        self.set_state('expanded', expanded)
        
    def render(self):
        """Render accordion"""
        container = Component()
        container.tag_name = "div"
        container.style.add(
            border="1px solid #e5e7eb",
            border_radius="0.5rem",
            overflow="hidden"
        )
        
        for i, item in enumerate(self.props['items']):
            # Item container
            item_container = Component()
            item_container.tag_name = "div"
            item_container.style.add(
                border_top="1px solid #e5e7eb" if i > 0 else "none"
            )
            
            # Header
            header = Component()
            header.tag_name = "button"
            header.style.add(
                width="100%",
                padding="1rem",
                background="none",
                border="none",
                text_align="left",
                cursor="pointer",
                display="flex",
                align_items="center",
                justify_content="space-between"
            )
            
            # Expand/collapse icon
            has_children = 'children' in item and item['children']
            if has_children:
                icon = Component()
                icon.tag_name = "span"
                icon.style.add(
                    margin_right="0.5rem",
                    transition="transform 0.2s"
                )
                if i in self.state['expanded']:
                    icon.style.add(transform="rotate(90deg)")
                icon.add(Element('span', text="▶"))
                header.add(icon)
                
            # Node icon (if provided)
            if 'icon' in item:
                node_icon = Component()
                node_icon.tag_name = "span"
                node_icon.style.add(margin_right="0.5rem")
                node_icon.add(Element('span', text=item['icon']))
                header.add(node_icon)
                
            # Node label
            label = Component()
            label.tag_name = "span"
            label.add(Element('span', text=item['label']))
            header.add(label)
            
            # Add click handler for expansion toggle
            if has_children:
                header.on('click', lambda: self._toggle_item(i))
                
            item_container.add(header)
            
            # Render children if node is expanded
            if has_children and i in self.state['expanded']:
                children_container = Component()
                for child in item['children']:
                    children_container.add(self._render_node(child, 1))
                item_container.add(children_container)
                
            container.add_child(item_container)
            
        return container

    def _render_node(self, node: Dict[str, Any], level: int = 0) -> Element:
        """Render a single node and its children"""
        node_container = Element('div')
        
        # Node header
        header = Element('div')
        header.style.add(
            display="flex",
            align_items="center",
            padding="0.5rem",
            padding_left=f"{level * 1.5 + 0.5}rem",
            cursor="pointer",
            transition="background-color 0.2s"
        )
        header.add_hover_style(background_color="#f5f5f5")
        
        # Expand/collapse icon
        has_children = 'children' in node and node['children']
        if has_children:
            icon = Element('span')
            icon.style.add(
                margin_right="0.5rem",
                transition="transform 0.2s"
            )
            if node['id'] in self.state['expanded']:
                icon.style.add(transform="rotate(90deg)")
            icon.add(Element('span', text="▶"))
            header.add(icon)
            
        # Node icon (if provided)
        if 'icon' in node:
            node_icon = Element('span')
            node_icon.style.add(margin_right="0.5rem")
            node_icon.add(Element('span', text=node['icon']))
            header.add(node_icon)
            
        # Node label
        label = Element('span')
        label.add(Element('span', text=node['label']))
        header.add(label)
        
        # Add click handler for expansion toggle
        if has_children:
            header.on('click', lambda: self._toggle_item(node['id']))
            
        node_container.add(header)
        
        # Render children if node is expanded
        if has_children and node['id'] in self.state['expanded']:
            children_container = Element('div')
            for child in node['children']:
                children_container.add(self._render_node(child, level + 1))
            node_container.add(children_container)
            
        return node_container

class VirtualList(Component):
    """虚拟滚动列表组件，用于高效渲染大量数据"""
    
    def __init__(self, 
                 items: List[Any],
                 render_item: Callable[[Any], Component],
                 item_height: int = 40,
                 container_height: int = 400,
                 buffer_size: int = 5):
        super().__init__()
        self.tag_name = "div"
        self.set_prop('items', items)
        self.set_prop('render_item', render_item)
        self.set_prop('item_height', item_height)
        self.set_prop('container_height', container_height)
        self.set_prop('buffer_size', buffer_size)
        
        self.state.update({
            'scroll_top': 0,
            'visible_items': [],
            'total_height': len(items) * item_height,
            'padding_top': 0,
            'padding_bottom': 0
        })
        
        self.style.add(
            height=f"{container_height}px",
            overflow_y="auto",
            position="relative"
        )
        
        self.on_scroll = EventDelegate()
        self.on_scroll.add(self._handle_scroll)
        
    def _handle_scroll(self, event: Dict[str, Any]):
        """处理滚动事件"""
        scroll_top = event['target'].scrollTop
        self._update_visible_items(scroll_top)
        
    def _update_visible_items(self, scroll_top: int):
        """更新可见项目列表"""
        self.state['scroll_top'] = scroll_top
        
        # 计算可见范围
        start_index = max(0, scroll_top // self.props['item_height'] - self.props['buffer_size'])
        visible_count = (self.props['container_height'] // self.props['item_height'] + 
                        2 * self.props['buffer_size'])
        end_index = min(len(self.props['items']), start_index + visible_count)
        
        # 更新可见项目
        self.state['visible_items'] = self.props['items'][start_index:end_index]
        
        # 更新padding以保持滚动位置
        self.state['padding_top'] = start_index * self.props['item_height']
        self.state['padding_bottom'] = (
            (len(self.props['items']) - end_index) * self.props['item_height']
        )
        
    def render(self):
        """渲染虚拟列表"""
        # 容器
        container = Component()
        container.tag_name = "div"
        container.style.add(
            height="100%",
            overflow_y="auto"
        )
        
        # 内容包装器
        content = Component()
        content.tag_name = "div"
        content.style.add(
            position="relative",
            height=f"{self.state['total_height']}px"
        )
        
        # 可见项目容器
        items_container = Component()
        items_container.tag_name = "div"
        items_container.style.add(
            position="absolute",
            top=f"{self.state['padding_top']}px",
            left="0",
            right="0"
        )
        
        # 渲染可见项目
        for item in self.state['visible_items']:
            rendered_item = self.props['render_item'](item)
            rendered_item.style.add(
                height=f"{self.props['item_height']}px"
            )
            items_container.add_child(rendered_item)
            
        content.add_child(items_container)
        container.add_child(content)
        
        return container

class DraggableList(Component):
    """可拖放的列表组件"""
    
    def __init__(self, 
                 items: list[Any],
                 render_item: Optional[Callable[[Any], Component]] = None,
                 on_reorder: Optional[Callable[[list[Any]], None]] = None):
        super().__init__()
        self.tag_name = "div"
        self.set_prop('items', items)
        self.set_prop('render_item', render_item or self._default_render_item)
        self.set_prop('on_reorder', on_reorder)
        
        self.state.update({
            'dragging_index': None,
            'drag_over_index': None,
            'items': items.copy()
        })
        
        # 设置容器样式
        self.style.add(
            position="relative",
            user_select="none"
        )
        
    def _default_render_item(self, item: Any) -> Component:
        """默认项渲染器"""
        text = Text(str(item))
        text.style.add(
            padding="1rem",
            background_color="#ffffff",
            border="1px solid #e0e0e0",
            margin_bottom="0.5rem",
            cursor="move"
        )
        return text
        
    def _handle_drag_start(self, index: int, event: dict[str, Any]):
        """处理拖拽开始事件"""
        try:
            self.state['dragging_index'] = index
            self._update()
        except Exception as e:
            self._logger.error(f"Error handling drag start: {e}", exc_info=True)
        
    def _handle_drag_over(self, index: int, event: dict[str, Any]):
        """处理拖拽悬停事件"""
        try:
            if index != self.state['drag_over_index']:
                self.state['drag_over_index'] = index
                self._update()
        except Exception as e:
            self._logger.error(f"Error handling drag over: {e}", exc_info=True)
        
    def _handle_drop(self, index: int, event: dict[str, Any]):
        """处理放置事件"""
        try:
            dragging_index = self.state['dragging_index']
            if dragging_index is not None and dragging_index != index:
                items = self.state['items']
                item = items.pop(dragging_index)
                items.insert(index, item)
                
                if self.props['on_reorder']:
                    self.props['on_reorder'](items)
                    
            self.state.update({
                'dragging_index': None,
                'drag_over_index': None
            })
            self._update()
            
        except Exception as e:
            self._logger.error(f"Error handling drop: {e}", exc_info=True)
        
    def render(self) -> Element:
        """渲染可拖放列表"""
        try:
            container = super().render()
            items = self.state['items']
            dragging_index = self.state['dragging_index']
            drag_over_index = self.state['drag_over_index']
            
            for i, item in enumerate(items):
                item_container = Element('div')
                item_container.style.add(
                    opacity="1" if i != dragging_index else "0.5",
                    transform="none" if i != drag_over_index else "translateY(8px)",
                    transition="transform 0.15s ease-in-out"
                )
                
                # 添加拖放事件监听器
                item_container.set_attribute('draggable', 'true')
                item_container.add_event_listener('dragstart', lambda e, i=i: self._handle_drag_start(i, e))
                item_container.add_event_listener('dragover', lambda e, i=i: self._handle_drag_over(i, e))
                item_container.add_event_listener('drop', lambda e, i=i: self._handle_drop(i, e))
                
                # 渲染项内容
                item_content = self.props['render_item'](item)
                item_container.append_child(item_content.render())
                
                container.append_child(item_container)
                
            return container
            
        except Exception as e:
            self._logger.error(f"Error rendering draggable list: {e}", exc_info=True)
            raise

class Table(Component):
    """表格组件"""
    
    def __init__(self, columns: list[dict[str, str]], data: list[dict[str, Any]],
                 sortable: bool = True, filterable: bool = True,
                 page_size: int = 10):
        super().__init__()
        self.tag_name = "div"
        self.set_prop('columns', columns)  # [{"key": "id", "title": "ID"}, ...]
        self.set_prop('data', data)
        self.set_prop('sortable', sortable)
        self.set_prop('filterable', filterable)
        self.set_prop('page_size', page_size)
        self.set_prop('current_page', 1)
        
        # State for sorting and filtering
        self.state['sort_key'] = None
        self.state['sort_order'] = 'asc'
        self.state['filters'] = {}
        
    def render(self):
        container = Element('div')
        
        # Create table element
        table = Element('table')
        table.style.add(
            width="100%",
            border_collapse="collapse",
            margin="1rem 0"
        )
        
        # Render header
        header = Element('thead')
        header_row = Element('tr')
        
        for col in self.props['columns']:
            th = Element('th')
            th.style.add(
                padding="0.75rem",
                border_bottom="2px solid #ddd",
                text_align="left",
                font_weight="bold"
            )
            
            if self.props['sortable']:
                sort_container = Element('div')
                sort_container.style.add(
                    display="flex",
                    align_items="center",
                    cursor="pointer"
                )
                sort_container.add(Element('span', text=col['title']))
                sort_container.add(Element('span', text="↕️", style={"margin-left": "0.5rem"}))
                th.add(sort_container)
            else:
                th.add(Element('span', text=col['title']))
                
            header_row.add(th)
            
        header.add(header_row)
        table.add(header)
        
        # Render body
        body = Element('tbody')
        
        # Apply pagination
        start_idx = (self.props['current_page'] - 1) * self.props['page_size']
        end_idx = start_idx + self.props['page_size']
        page_data = self.props['data'][start_idx:end_idx]
        
        for row_data in page_data:
            tr = Element('tr')
            tr.style.add(
                border_bottom="1px solid #ddd",
                transition="background-color 0.2s"
            )
            tr.add_hover_style(background_color="#f5f5f5")
            
            for col in self.props['columns']:
                td = Element('td')
                td.style.add(padding="0.75rem")
                td.add(Element('span', text=str(row_data.get(col['key'], ''))))
                tr.add(td)
                
            body.add(tr)
            
        table.add(body)
        container.add(table)
        
        # Add pagination
        if len(self.props['data']) > self.props['page_size']:
            pagination = self._render_pagination()
            container.add(pagination)
        
        return container
        
    def _render_pagination(self):
        total_pages = (len(self.props['data']) + self.props['page_size'] - 1) // self.props['page_size']
        
        pagination = Element('div')
        pagination.style.add(
            display="flex",
            justify_content="center",
            align_items="center",
            margin_top="1rem"
        )
        
        # Previous button
        prev_btn = Element('button')
        prev_btn.add(Element('span', text="Previous"))
        prev_btn.style.add(
            padding="0.5rem 1rem",
            margin="0 0.25rem",
            border="1px solid #ddd",
            border_radius="4px",
            cursor="pointer" if self.props['current_page'] > 1 else "not-allowed",
            background_color="#fff"
        )
        pagination.add(prev_btn)
        
        # Page numbers
        for page in range(1, total_pages + 1):
            page_btn = Element('button')
            page_btn.add(Element('span', text=str(page)))
            page_btn.style.add(
                padding="0.5rem 1rem",
                margin="0 0.25rem",
                border="1px solid #ddd",
                border_radius="4px",
                cursor="pointer",
                background_color="#fff" if page != self.props['current_page'] else "#e6e6e6"
            )
            pagination.add(page_btn)
            
        # Next button
        next_btn = Element('button')
        next_btn.add(Element('span', text="Next"))
        next_btn.style.add(
            padding="0.5rem 1rem",
            margin="0 0.25rem",
            border="1px solid #ddd",
            border_radius="4px",
            cursor="pointer" if self.props['current_page'] < total_pages else "not-allowed",
            background_color="#fff"
        )
        pagination.add(next_btn)
        
        return pagination

class Tree(Component):
    """树形组件"""
    def __init__(self, data: List[Dict[str, Any]], expanded: bool = False):
        """
        初始化树形组件
        data: 树形数据，每个节点是一个字典，包含'id'、'label'、'children'等键
        """
        super().__init__()
        self.tag_name = "div"
        self.set_prop('data', data)
        self.state['expanded'] = set()  # Store expanded node IDs
        
        # Expand all nodes if expanded is True
        if expanded:
            self._expand_all(data)
            
    def _expand_all(self, nodes: List[Dict[str, Any]]) -> None:
        """递归展开所有节点"""
        for node in nodes:
            self.state['expanded'].add(node['id'])
            if node.get('children'):
                self._expand_all(node['children'])
                
    def toggle_node(self, node_id: str) -> None:
        """Toggle node expansion state"""
        if node_id in self.state['expanded']:
            self.state['expanded'].remove(node_id)
        else:
            self.state['expanded'].add(node_id)
        self._update()
        
    def _render_node(self, node: Dict[str, Any], level: int = 0) -> Element:
        """Render a single node and its children"""
        node_container = Element('div')
        
        # Node header
        header = Element('div')
        header.style.add(
            display="flex",
            align_items="center",
            padding="0.5rem",
            padding_left=f"{level * 1.5 + 0.5}rem",
            cursor="pointer",
            transition="background-color 0.2s"
        )
        header.add_hover_style(background_color="#f5f5f5")
        
        # Expand/collapse icon
        has_children = 'children' in node and node['children']
        if has_children:
            icon = Element('span')
            icon.style.add(
                margin_right="0.5rem",
                transition="transform 0.2s"
            )
            if node['id'] in self.state['expanded']:
                icon.style.add(transform="rotate(90deg)")
            icon.add(Element('span', text="▶"))
            header.add(icon)
            
        # Node icon (if provided)
        if 'icon' in node:
            node_icon = Element('span')
            node_icon.style.add(margin_right="0.5rem")
            node_icon.add(Element('span', text=node['icon']))
            header.add(node_icon)
            
        # Node label
        label = Element('span')
        label.add(Element('span', text=node['label']))
        header.add(label)
        
        # Add click handler for expansion toggle
        if has_children:
            header.on('click', lambda: self.toggle_node(node['id']))
            
        node_container.add(header)
        
        # Render children if node is expanded
        if has_children and node['id'] in self.state['expanded']:
            children_container = Element('div')
            for child in node['children']:
                children_container.add(self._render_node(child, level + 1))
            node_container.add(children_container)
            
        return node_container
        
    def render(self):
        container = Element('div')
        container.style.add(
            border="1px solid #ddd",
            border_radius="4px",
            overflow="hidden"
        )
        
        # Render each root node
        for node in self.props['data']:
            container.add(self._render_node(node))
            
        return container

class Responsive(Component):
    """响应式容器组件"""
    breakpoints = {
        'sm': '576px',
        'md': '768px',
        'lg': '992px',
        'xl': '1200px',
        'xxl': '1400px'
    }
    
    def __init__(self):
        super().__init__()
        self.tag_name = "div"
        self.style.add(
            width="100%",
            margin="0 auto",
            padding="0 15px",
            box_sizing="border-box"
        )
        
    def add_media_query(self, breakpoint: str, styles: dict[str, str]):
        self.style.add_media_query(
            f"(min-width: {self.breakpoints[breakpoint]})",
            styles
        )
        return self

class Skeleton(Component):
    """骨架屏组件"""
    def __init__(self, type: str = "text", rows: int = 1, height: str = "1rem"):
        super().__init__()
        self.tag_name = "div"
        self.set_prop('type', type)
        self.set_prop('rows', rows)
        self.set_prop('height', height)
        self.style.add(
            background="linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)",
            background_size="200% 100%",
            animation="skeleton-loading 1.5s infinite",
            border_radius="4px",
            height=height,
            margin_bottom="0.5rem"
        )

class Carousel(Component):
    """幻灯片组件"""
    def __init__(self, images: list[dict[str, str]], auto_play: bool = True, interval: int = 3000):
        super().__init__()
        self.tag_name = "div"
        self.set_prop('images', images)  # [{"src": "...", "alt": "..."}]
        self.set_prop('auto_play', auto_play)
        self.set_prop('interval', interval)
        self.state['current_index'] = 0
        self.style.add(
            position="relative",
            overflow="hidden",
            width="100%",
            height="100%"
        )

class Drawer(Component):
    """抽屉组件"""
    def __init__(self, content: Component, position: str = "left", width: str = "300px"):
        super().__init__()
        self.tag_name = "div"
        self.set_prop('content', content)
        self.set_prop('position', position)
        self.set_prop('width', width)
        self.state['visible'] = False
        self.style.add(
            position="fixed",
            top="0",
            height="100%",
            background_color="#ffffff",
            box_shadow="0 0 10px rgba(0,0,0,0.1)",
            transition="transform 0.3s ease-in-out",
            z_index="1000"
        )

class Progress(Component):
    """进度条组件"""
    def __init__(self, value: int = 0, max: int = 100, type: str = "bar", color: str = "#007bff"):
        super().__init__()
        self.tag_name = "div"
        self.set_prop('value', value)
        self.set_prop('max', max)
        self.set_prop('type', type)
        self.set_prop('color', color)
        self.style.add(
            width="100%",
            height="0.5rem",
            background_color="#e9ecef",
            border_radius="0.25rem",
            overflow="hidden"
        )

class Badge(Component):
    """徽章组件"""
    def __init__(self, text: str, type: str = "primary", pill: bool = False):
        super().__init__()
        self.tag_name = "span"
        self.set_prop('text', text)
        self.set_prop('type', type)
        self.set_prop('pill', pill)
        self.style.add(
            display="inline-block",
            padding="0.25em 0.4em",
            font_size="75%",
            font_weight="700",
            line_height="1",
            text_align="center",
            white_space="nowrap",
            vertical_align="baseline",
            border_radius="0.25rem" if not pill else "10rem",
            color="#fff",
            background_color=self._get_type_color(type)
        )

    def _get_type_color(self, type: str) -> str:
        colors = {
            'primary': '#007bff',
            'secondary': '#6c757d',
            'success': '#28a745',
            'danger': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8'
        }
        return colors.get(type, colors['primary'])

class Tooltip(Component):
    """提示框组件"""
    def __init__(self, content: str, position: str = "top"):
        super().__init__()
        self.tag_name = "div"
        self.set_prop('content', content)
        self.set_prop('position', position)
        self.style.add(
            position="relative",
            display="inline-block"
        )
