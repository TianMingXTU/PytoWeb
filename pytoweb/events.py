"""
PytoWeb事件系统

提供事件处理、委托、批处理和状态管理功能。
"""

from __future__ import annotations
from typing import (
    Dict, Any, Optional, Callable, List, Set,
    TypeVar, TypedDict, Union
)
from collections import defaultdict
import asyncio
import time
import uuid
import json
import weakref
import logging
from concurrent.futures import ThreadPoolExecutor

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 类型别名
T = TypeVar('T')
EventType = str
HandlerType = Callable[..., None]
EventData = Dict[str, Any]

class Event:
    """事件基类"""
    def __init__(self, event_type: EventType, target: Any, data: EventData | None = None):
        self.type = event_type
        self.target = target
        self.data = data or {}
        self.timestamp = time.time()
        self.propagation_stopped = False
        self.default_prevented = False
        
    def stop_propagation(self):
        """停止事件传播"""
        self.propagation_stopped = True
        
    def prevent_default(self):
        """阻止默认行为"""
        self.default_prevented = True

class EventHandler:
    """事件处理器"""
    def __init__(self, 
                 callback: Callable[[Event], None],
                 once: bool = False,
                 capture: bool = False,
                 passive: bool = False):
        self.callback = callback
        self.once = once
        self.capture = capture
        self.passive = passive

class EventBridge:
    """Python和JavaScript事件桥接器"""
    
    _handlers: Dict[str, Callable] = {}
    _js_code = """
    window.pytoweb = {
        handlers: {},
        
        handleEvent: function(handlerId, event) {
            // 发送事件数据到Python
            const eventData = {
                type: event.type,
                target: {
                    id: event.target.id,
                    value: event.target.value,
                    checked: event.target.checked,
                    dataset: event.target.dataset,
                    scrollTop: event.target.scrollTop,
                    scrollHeight: event.target.scrollHeight,
                    clientHeight: event.target.clientHeight
                },
                clientX: event.clientX,
                clientY: event.clientY,
                timestamp: Date.now()
            };
            
            // 发送到Python后端
            this.sendToPython(handlerId, eventData);
        },
        
        sendToPython: async function(handlerId, data) {
            try {
                const response = await fetch('/api/events', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        handlerId: handlerId,
                        data: data
                    })
                });
                
                if (!response.ok) {
                    throw new Error('Event handling failed');
                }
            } catch (error) {
                console.error('Error sending event to Python:', error);
            }
        },
        
        registerHandler: function(handlerId, options = {}) {
            const handler = (event) => {
                if (options.preventDefault) {
                    event.preventDefault();
                }
                if (options.stopPropagation) {
                    event.stopPropagation();
                }
                this.handleEvent(handlerId, event);
            };
            
            this.handlers[handlerId] = handler;
            return handler;
        },
        
        removeHandler: function(handlerId) {
            delete this.handlers[handlerId];
        }
    };
    """
    
    @classmethod
    def register_handler(cls, handler: Callable) -> str:
        """注册事件处理器并返回处理器ID"""
        handler_id = str(uuid.uuid4())
        cls._handlers[handler_id] = handler
        return handler_id
        
    @classmethod
    def remove_handler(cls, handler_id: str):
        """移除事件处理器"""
        if handler_id in cls._handlers:
            del cls._handlers[handler_id]
            
    @classmethod
    def handle_event(cls, handler_id: str, event_data: Dict[str, Any]):
        """处理从JavaScript发来的事件"""
        if handler_id in cls._handlers:
            try:
                event = Event(
                    event_type=event_data.get('type', ''),
                    target=event_data.get('target', {}),
                    data=event_data
                )
                cls._handlers[handler_id](event)
            except Exception as e:
                logger.error(f"Error handling event: {e}", exc_info=True)

class EventDelegate:
    """事件委托类"""
    def __init__(self):
        self._handlers: list[HandlerType] = []
        self._logger = logging.getLogger(__name__)
        
    def add(self, handler: HandlerType):
        """添加事件处理器"""
        if handler not in self._handlers:
            self._handlers.append(handler)
        
    def remove(self, handler: HandlerType):
        """移除事件处理器"""
        if handler in self._handlers:
            self._handlers.remove(handler)
            
    def clear(self):
        """清除所有处理器"""
        self._handlers.clear()
        
    def __call__(self, *args, **kwargs):
        """调用所有处理器"""
        for handler in self._handlers:
            try:
                handler(*args, **kwargs)
            except Exception as e:
                self._logger.error(f"Error in event handler: {e}", exc_info=True)

class EventEmitter:
    """增强的事件发射器，支持事件委托和批处理"""
    
    def __init__(self):
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)
        self._delegate_handlers: dict[str, dict[str, list[EventHandler]]] = defaultdict(lambda: defaultdict(list))
        self._batch_handlers: dict[str, list[Callable[[list[Event]], None]]] = defaultdict(list)
        self._batch_queue: dict[str, list[Event]] = defaultdict(list)
        self._batch_timeout = 16.67  # ~60fps
        self._logger = logging.getLogger(__name__)
        
    def on(self, event_type: str, callback: Callable[[Event], None], selector: str | None = None, **options):
        """添加事件监听器"""
        handler = EventHandler(callback, **options)
        
        if selector:
            self._delegate_handlers[event_type][selector].append(handler)
        else:
            self._handlers[event_type].append(handler)
            
    def off(self, event_type: str, callback: Callable[[Event], None] | None = None, selector: str | None = None):
        """移除事件监听器"""
        if selector:
            if callback:
                self._delegate_handlers[event_type][selector] = [
                    h for h in self._delegate_handlers[event_type][selector]
                    if h.callback != callback
                ]
            else:
                self._delegate_handlers[event_type][selector].clear()
        else:
            if callback:
                self._handlers[event_type] = [
                    h for h in self._handlers[event_type]
                    if h.callback != callback
                ]
            else:
                self._handlers[event_type].clear()
                
    def emit(self, event: Event):
        """发射事件"""
        if event.propagation_stopped:
            return
            
        # 处理直接监听器
        for handler in self._handlers[event.type]:
            try:
                if handler.once:
                    self.off(event.type, handler.callback)
                handler.callback(event)
            except Exception as e:
                self._logger.error(f"Error in event handler: {e}", exc_info=True)
                
        # 处理委托监听器
        if isinstance(event.target, dict) and 'id' in event.target:
            target_id = event.target['id']
            for selector, handlers in self._delegate_handlers[event.type].items():
                if self._matches_selector(target_id, selector):
                    for handler in handlers:
                        try:
                            if handler.once:
                                self.off(event.type, handler.callback, selector)
                            handler.callback(event)
                        except Exception as e:
                            self._logger.error(f"Error in delegate handler: {e}", exc_info=True)
                            
        # 添加到批处理队列
        if event.type in self._batch_handlers:
            self._batch_queue[event.type].append(event)
            self._schedule_batch_process(event.type)
            
    def _matches_selector(self, target_id: str, selector: str) -> bool:
        """检查目标是否匹配选择器"""
        # 简单的选择器匹配实现
        return selector.startswith('#') and target_id == selector[1:]
        
    def add_batch_handler(self, event_type: str, handler: Callable[[list[Event]], None]):
        """添加批处理事件处理器"""
        self._batch_handlers[event_type].append(handler)
        
    def _schedule_batch_process(self, event_type: str):
        """调度批处理"""
        async def process_batch():
            await asyncio.sleep(self._batch_timeout / 1000)
            events = self._batch_queue[event_type]
            self._batch_queue[event_type] = []
            
            for handler in self._batch_handlers[event_type]:
                try:
                    handler(events)
                except Exception as e:
                    self._logger.error(f"Error in batch handler: {e}", exc_info=True)
                    
        asyncio.create_task(process_batch())

class EventManager:
    """全局事件管理系统"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
        
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.emitter = EventEmitter()
            self._listeners: Dict[str, Set[weakref.ref]] = defaultdict(set)
            self._logger = logging.getLogger(__name__)
            self.initialized = True
            
    def add_listener(self, target: Any, event_type: str):
        """添加全局事件监听器"""
        ref = weakref.ref(target, lambda r: self._cleanup_listener(r, event_type))
        self._listeners[event_type].add(ref)
        
    def remove_listener(self, target: Any, event_type: str):
        """移除全局事件监听器"""
        to_remove = None
        for ref in self._listeners[event_type]:
            if ref() is target:
                to_remove = ref
                break
        if to_remove:
            self._listeners[event_type].remove(to_remove)
            
    def _cleanup_listener(self, ref: weakref.ref, event_type: str):
        """清理失效的监听器"""
        self._listeners[event_type].discard(ref)
        
    def dispatch_event(self, event: Event, batch: bool = False):
        """分发事件到所有监听器"""
        try:
            if batch:
                self.emitter.add_batch_handler(event.type, lambda events: self._dispatch_batch(events))
                self.emitter.emit(event)
            else:
                self._dispatch_single(event)
        except Exception as e:
            self._logger.error(f"Error dispatching event: {e}", exc_info=True)
            
    def _dispatch_single(self, event: Event):
        """分发单个事件"""
        for ref in list(self._listeners[event.type]):
            target = ref()
            if target is not None:
                try:
                    target.handle_event(event)
                except Exception as e:
                    self._logger.error(f"Error in event handler: {e}", exc_info=True)
                    
    def _dispatch_batch(self, events: List[Event]):
        """分发事件批次"""
        if not events:
            return
            
        event_type = events[0].type
        for ref in list(self._listeners[event_type]):
            target = ref()
            if target is not None:
                try:
                    target.handle_event_batch(events)
                except Exception as e:
                    self._logger.error(f"Error in batch event handler: {e}", exc_info=True)
                    
    def dispatch_batch(self, events: List[Event]):
        """一次性分发多个事件"""
        for event in events:
            self.dispatch_event(event, batch=True)

class StateManager:
    """状态管理系统"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
        
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self._state: dict[str, Any] = {}
            self._listeners: dict[str, list[Callable[[Any], None]]] = defaultdict(list)
            self._batch_updates = False
            self._pending_updates: dict[str, Any] = {}
            self._logger = logging.getLogger(__name__)
            self.initialized = True
            
    def set_state(self, key: str, value: Any):
        """设置状态值"""
        try:
            if self._batch_updates:
                self._pending_updates[key] = value
            else:
                old_value = self._state.get(key)
                if old_value != value:
                    self._state[key] = value
                    self._notify_listeners(key)
        except Exception as e:
            self._logger.error(f"Error setting state: {e}", exc_info=True)
            
    def get_state(self, key: str, default: Any | None = None) -> Any:
        """获取状态值"""
        return self._state.get(key, default)
        
    def subscribe(self, key: str, listener: Callable[[Any], None]):
        """订阅状态变化"""
        if listener not in self._listeners[key]:
            self._listeners[key].append(listener)
            
    def unsubscribe(self, key: str, listener: Callable[[Any], None]):
        """取消订阅状态变化"""
        if listener in self._listeners[key]:
            self._listeners[key].remove(listener)
            
    def _notify_listeners(self, key: str):
        """通知状态变化的监听器"""
        value = self._state.get(key)
        for listener in self._listeners[key]:
            try:
                listener(value)
            except Exception as e:
                self._logger.error(f"Error notifying state listener: {e}", exc_info=True)
                
    def batch_update(self, updates: dict[str, Any]):
        """批量更新多个状态值"""
        self._batch_updates = True
        try:
            for key, value in updates.items():
                self.set_state(key, value)
            for key in self._pending_updates:
                self._state[key] = self._pending_updates[key]
                self._notify_listeners(key)
        finally:
            self._batch_updates = False
            self._pending_updates.clear()
