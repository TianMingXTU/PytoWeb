# PytoWeb State Management | PytoWeb 状态管理

PytoWeb provides a powerful state management system with support for reactive updates, persistence, and time-based expiration.

## Basic Usage | 基本用法

```python
from pytoweb.state import Store

# Create store
store = Store()

# Set state
store.set("user.name", "John")
store.set("user.age", 30)

# Get state
name = store.get("user.name")  # "John"
age = store.get("user.age")    # 30

# Get with default value
email = store.get("user.email", "default@email.com")
```

## State Reactivity | 状态响应

Subscribe to state changes:

```python
def on_name_change(change):
    print(f"Name changed from {change.old_value} to {change.new_value}")

# Subscribe to specific path
store.subscribe("user.name", on_name_change)

# Update triggers callback
store.set("user.name", "Jane")  # Prints: Name changed from John to Jane

# Unsubscribe
store.unsubscribe("user.name", on_name_change)
```

## Persistent State | 持久化状态

Store state that persists across sessions:

```python
from pytoweb.state import PersistentStore

# Create persistent store
store = PersistentStore("app_state.json")

# State is automatically saved
store.set("settings.theme", "dark")
store.set("settings.language", "en")

# State persists after restart
theme = store.get("settings.theme")  # "dark"
```

## State Manager | 状态管理器

Use the global state manager for application-wide state:

```python
from pytoweb.state import StateManager

# Get singleton instance
state = StateManager.get_instance()

# Set state with TTL (time-to-live)
state.set("session.token", "abc123")  # Default TTL: 1 hour

# Watch multiple paths
def on_settings_change(change):
    print(f"Settings changed: {change.path}")

state.watch(
    paths=["settings.theme", "settings.language"],
    callback=on_settings_change
)

# Unwatch paths
state.unwatch(
    paths=["settings.theme", "settings.language"],
    callback=on_settings_change
)
```

## Integration with Components | 与组件集成

Use state management in components:

```python
from pytoweb.components import Component
from pytoweb.state import StateManager

class Counter(Component):
    def __init__(self):
        super().__init__()
        self.state = StateManager.get_instance()
        self.state.set("counter", 0)
        
    def increment(self):
        current = self.state.get("counter")
        self.state.set("counter", current + 1)
        
    def render(self):
        count = self.state.get("counter")
        return {
            "tag": "div",
            "children": [
                f"Count: {count}",
                {
                    "tag": "button",
                    "props": {"onClick": self.increment},
                    "children": ["Increment"]
                }
            ]
        }
```

## State Change Events | 状态变更事件

The `StateChange` event provides detailed information about state changes:

```python
from pytoweb.state import StateChange

def log_changes(change: StateChange):
    print(f"""
    Path: {change.path}
    Old Value: {change.old_value}
    New Value: {change.new_value}
    """)

store.subscribe("user", log_changes)
```

## Nested State | 嵌套状态

Handle complex nested state structures:

```python
# Set nested state
store.set("app.user.profile.settings.notifications", {
    "email": True,
    "push": False
})

# Access nested state
notifications = store.get("app.user.profile.settings.notifications")

# Subscribe to nested changes
store.subscribe("app.user.profile", on_profile_change)
```

## State Persistence | 状态持久化

Create multiple persistent stores:

```python
state_manager = StateManager.get_instance()

# Create named persistent stores
state_manager.create_persistent_store("user", "user_state.json")
state_manager.create_persistent_store("app", "app_state.json")

# State is automatically persisted
state_manager.set("user.preferences.theme", "light")
```

## Best Practices | 最佳实践

1. Use descriptive state paths
2. Keep state normalized
3. Subscribe to specific paths instead of root state
4. Clean up subscriptions when components unmount
5. Use TTL for temporary state
6. Handle state loading and error states

## Performance Considerations | 性能考虑

1. State updates are thread-safe
2. Use batch updates for multiple changes
3. Consider TTL for cache-like state
4. Subscribe to specific paths for better performance
5. Clean up expired state periodically
