# PytoWeb Event System | PytoWeb 事件系统

PytoWeb provides a powerful event system that handles both Python and JavaScript events, with support for event delegation, batching, and state management.

## Core Components | 核心组件

### Event Class | 事件类

The base class for all events in PytoWeb:

```python
from pytoweb.events import Event

# Create an event
event = Event(
    event_type="click",
    target=button_element,
    data={"x": 100, "y": 200}
)

# Control event flow
event.stop_propagation()  # Stop event bubbling
event.prevent_default()   # Prevent default behavior
```

### EventHandler | 事件处理器

Configure how events are handled:

```python
from pytoweb.events import EventHandler

# Create an event handler
handler = EventHandler(
    callback=lambda e: print(f"Event: {e.type}"),
    once=True,           # Only trigger once
    capture=False,       # Use bubbling phase
    passive=True         # Don't call preventDefault()
)
```

### EventBridge | 事件桥接器

Bridges Python and JavaScript events:

```python
from pytoweb.events import EventBridge

# Register a Python handler for JavaScript events
@EventBridge.register("click")
def handle_click(event_data):
    print(f"Click at: {event_data['clientX']}, {event_data['clientY']}")

# Available event data from JavaScript
event_data = {
    "type": "click",
    "target": {
        "id": "button-1",
        "value": "Click me",
        "checked": False,
        "dataset": {},
        "scrollTop": 0,
        "scrollHeight": 100,
        "clientHeight": 50
    },
    "clientX": 100,
    "clientY": 200,
    "timestamp": 1234567890
}
```

### EventDelegate | 事件委托

Efficiently handle events for multiple elements:

```python
from pytoweb.events import EventDelegate

# Create a delegate
delegate = EventDelegate()

# Add handlers
def on_click(event):
    print(f"Clicked: {event.target.id}")

delegate.add(on_click)

# Remove handler
delegate.remove(on_click)

# Clear all handlers
delegate.clear()
```

### EventEmitter | 事件发射器

Enhanced event emitter with delegation and batching support:

```python
from pytoweb.events import EventEmitter

emitter = EventEmitter()

# Add event listener
emitter.on("click", 
    callback=lambda e: print("Clicked!"),
    selector=".button",  # Only for elements matching selector
    once=True,          # Remove after first trigger
    capture=False,      # Use bubbling phase
    passive=True        # Don't call preventDefault()
)

# Remove listener
emitter.off("click", callback)

# Emit event
emitter.emit(Event("click", target=button))

# Batch processing
emitter.add_batch_handler("scroll", 
    lambda events: print(f"Processed {len(events)} scroll events")
)
```

### EventManager | 事件管理器

Global event management system:

```python
from pytoweb.events import EventManager

manager = EventManager()

# Add global listener
manager.add_listener(component, "click")

# Remove listener
manager.remove_listener(component, "click")

# Dispatch single event
manager.dispatch_event(event)

# Batch dispatch
events = [event1, event2, event3]
manager.dispatch_batch(events)
```

## Event Flow | 事件流

Events in PytoWeb follow a similar flow to DOM events:

1. **Capture Phase**: Events travel from root to target
2. **Target Phase**: Event reaches target element
3. **Bubble Phase**: Events bubble up from target to root

```python
# Capture phase handler
emitter.on("click", handler, capture=True)

# Bubble phase handler (default)
emitter.on("click", handler)
```

## Performance Optimization | 性能优化

### Event Delegation | 事件委托

Instead of attaching handlers to each element, use delegation:

```python
# Bad: Individual handlers
for button in buttons:
    emitter.on("click", handler, target=button)

# Good: Use delegation
emitter.on("click", handler, selector=".button")
```

### Event Batching | 事件批处理

Batch process high-frequency events:

```python
# Add batch handler for scroll events
emitter.add_batch_handler("scroll", process_scroll_batch)

# Batch processing happens automatically every ~16.67ms (60fps)
def process_scroll_batch(events):
    # Process multiple scroll events at once
    final_scroll_position = events[-1].data["scrollTop"]
    update_scroll_indicator(final_scroll_position)
```

### Weak References | 弱引用

The event system uses weak references to prevent memory leaks:

```python
# Listeners are automatically cleaned up when components are destroyed
manager.add_listener(component, "click")
```

## State Integration | 状态集成

Events can trigger state updates:

```python
from pytoweb.state import StateManager

class Counter(Component):
    def __init__(self):
        self.state = StateManager({"count": 0})
        
    def handle_click(self, event):
        self.state.update({"count": self.state["count"] + 1})
        
    def render(self):
        return Button(
            text=f"Count: {self.state['count']}",
            on_click=self.handle_click
        )
```

## Best Practices | 最佳实践

1. Use event delegation for similar elements
2. Batch process high-frequency events
3. Keep event handlers small and focused
4. Clean up event listeners when components unmount
5. Use weak references to prevent memory leaks
6. Leverage the event system's built-in performance optimizations
