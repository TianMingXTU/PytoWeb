# Event System | 事件系统

PytoWeb provides a powerful event system that handles both DOM events and custom events.
PytoWeb 提供了一个强大的事件系统，可以处理 DOM 事件和自定义事件。

## EventHandler

The `EventHandler` class is the base class for all event handlers.
`EventHandler` 类是所有事件处理器的基类。

```python
from pytoweb.events import EventHandler

class EventHandler:
    def __init__(self, event_type: str, callback: Callable):
        self.event_type = event_type
        self.callback = callback
```

### Built-in Event Types | 内置事件类型

```python
# Mouse Events | 鼠标事件
CLICK = 'click'
DBLCLICK = 'dblclick'
MOUSEDOWN = 'mousedown'
MOUSEUP = 'mouseup'
MOUSEMOVE = 'mousemove'
MOUSEENTER = 'mouseenter'
MOUSELEAVE = 'mouseleave'

# Keyboard Events | 键盘事件
KEYDOWN = 'keydown'
KEYUP = 'keyup'
KEYPRESS = 'keypress'

# Form Events | 表单事件
SUBMIT = 'submit'
CHANGE = 'change'
INPUT = 'input'
FOCUS = 'focus'
BLUR = 'blur'

# Document Events | 文档事件
LOAD = 'load'
UNLOAD = 'unload'
RESIZE = 'resize'
SCROLL = 'scroll'
```

## Event

The `Event` class represents an event in the system.
`Event` 类代表系统中的一个事件。

```python
from pytoweb.events import Event

class Event:
    def __init__(self, event_type: str, target: Any = None, data: Dict = None):
        self.type = event_type
        self.target = target
        self.data = data or {}
        self.timestamp = time.time()
```

### Event Properties | 事件属性

```python
event = Event('click', button_element)
print(event.type)      # 'click'
print(event.target)    # <Button element>
print(event.data)      # {}
print(event.timestamp) # 1234567890.123
```

## EventEmitter

The `EventEmitter` class provides event emission and subscription capabilities.
`EventEmitter` 类提供事件发射和订阅功能。

```python
from pytoweb.events import EventEmitter

class EventEmitter:
    def __init__(self):
        self._handlers: Dict[str, List[EventHandler]] = {}
```

### Methods | 方法

#### Adding Event Handlers | 添加事件处理器

```python
# Basic usage | 基础用法
emitter = EventEmitter()
emitter.on('click', lambda e: print('Clicked!'))

# With decorator | 使用装饰器
@emitter.on('click')
def handle_click(event):
    print('Clicked!')

# One-time handler | 一次性处理器
emitter.once('load', lambda e: print('Loaded!'))
```

#### Removing Event Handlers | 移除事件处理器

```python
# Remove specific handler | 移除特定处理器
emitter.off('click', handler)

# Remove all handlers for event | 移除事件所有处理器
emitter.off('click')

# Remove all handlers | 移除所有处理器
emitter.clear()
```

#### Emitting Events | 发射事件

```python
# Basic event | 基础事件
emitter.emit('click')

# Event with data | 带数据事件
emitter.emit('change', {'value': 'new value'})

# Async event emission | 异步事件发射
await emitter.emit_async('load')
```

## Component Event Integration | 组件事件集成

Example of using events in a component:
在组件中使用事件的示例：

```python
from pytoweb.components import Component
from pytoweb.events import EventEmitter

class Button(Component):
    def __init__(self):
        super().__init__()
        self.events = EventEmitter()
        
    def on_click(self, event):
        self.events.emit('click', {
            'target': self,
            'x': event.x,
            'y': event.y
        })
        
    def render(self):
        return {
            'tag': 'button',
            'props': {
                'onClick': self.on_click
            },
            'children': ['Click me']
        }
```

## Event Delegation | 事件委托

Example of event delegation pattern:
事件委托模式示例：

```python
class Container(Component):
    def __init__(self):
        super().__init__()
        self.events = EventEmitter()
        
    def handle_child_event(self, event):
        # Delegate event to appropriate handler
        child_id = event.target.id
        if child_id in self.child_handlers:
            self.child_handlers[child_id](event)
            
    def render(self):
        return {
            'tag': 'div',
            'props': {
                'onClick': self.handle_child_event
            },
            'children': [
                # Child components
            ]
        }
```

## Custom Events | 自定义事件

Creating and using custom events:
创建和使用自定义事件：

```python
# Define custom event | 定义自定义事件
class DataLoadEvent(Event):
    def __init__(self, data: Dict):
        super().__init__('data-load', data=data)
        self.success = data.get('success', True)
        self.payload = data.get('payload')

# Use custom event | 使用自定义事件
class DataComponent(Component):
    def __init__(self):
        super().__init__()
        self.events = EventEmitter()
        
    async def load_data(self):
        try:
            data = await fetch_data()
            event = DataLoadEvent({
                'success': True,
                'payload': data
            })
        except Exception as e:
            event = DataLoadEvent({
                'success': False,
                'error': str(e)
            })
        self.events.emit(event)
```

## Event Middleware | 事件中间件

Example of event middleware for logging:
事件中间件示例（日志）：

```python
class EventLogger:
    def __init__(self, emitter: EventEmitter):
        self.emitter = emitter
        
    def __call__(self, event: Event, next_handler: Callable):
        print(f"Event: {event.type} at {event.timestamp}")
        result = next_handler(event)
        print(f"Event handled: {event.type}")
        return result

# Usage | 使用
emitter = EventEmitter()
logger = EventLogger(emitter)
emitter.use(logger)
```

## Performance Considerations | 性能考虑

1. **Event Debouncing** | 事件防抖
```python
from pytoweb.utils import debounce

@debounce(wait_ms=100)
def handle_resize(event):
    # Handle resize event
    pass
```

2. **Event Throttling** | 事件节流
```python
from pytoweb.utils import throttle

@throttle(wait_ms=50)
def handle_scroll(event):
    # Handle scroll event
    pass
```

3. **Event Pooling** | 事件池
```python
class EventPool:
    def __init__(self, size: int = 10):
        self.pool = [Event(None) for _ in range(size)]
        self.index = 0
        
    def get(self, event_type: str, data: Dict = None) -> Event:
        event = self.pool[self.index]
        event.type = event_type
        event.data = data
        self.index = (self.index + 1) % len(self.pool)
        return event
```
