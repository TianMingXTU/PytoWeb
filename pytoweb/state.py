"""State management system for PytoWeb."""
from typing import Dict, List, Any, Callable
import json
import threading
import time
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class StateChange:
    """Represents a state change event."""
    path: str
    old_value: Any
    new_value: Any

class Store:
    """Central state store with reactive updates."""
    
    def __init__(self):
        self._state = {}
        self._subscribers = defaultdict(list)
        self._lock = threading.Lock()
        
    def get(self, path: str, default: Any = None) -> Any:
        """Get state value at path."""
        try:
            keys = path.split('.')
            value = self._state
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
            
    def set(self, path: str, value: Any):
        """Set state value at path."""
        with self._lock:
            keys = path.split('.')
            target = self._state
            
            # Navigate to the parent of the target
            for key in keys[:-1]:
                if key not in target:
                    target[key] = {}
                target = target[key]
            
            # Get old value and set new value
            old_value = target.get(keys[-1])
            target[keys[-1]] = value
            
            # Notify subscribers
            change = StateChange(path, old_value, value)
            self._notify_subscribers(change)
            
    def subscribe(self, path: str, callback: Callable[[StateChange], None]):
        """Subscribe to state changes at path."""
        with self._lock:
            self._subscribers[path].append(callback)
            
    def unsubscribe(self, path: str, callback: Callable[[StateChange], None]):
        """Unsubscribe from state changes at path."""
        with self._lock:
            if path in self._subscribers:
                self._subscribers[path].remove(callback)
                
    def _notify_subscribers(self, change: StateChange):
        """Notify all relevant subscribers of state change."""
        # Notify exact path subscribers
        for callback in self._subscribers[change.path]:
            callback(change)
            
        # Notify parent path subscribers
        parts = change.path.split('.')
        for i in range(len(parts)):
            parent_path = '.'.join(parts[:i])
            if parent_path:
                for callback in self._subscribers[parent_path]:
                    callback(change)

class PersistentStore(Store):
    """Store with persistence capabilities."""
    
    def __init__(self, storage_path: str):
        super().__init__()
        self.storage_path = storage_path
        self._load_state()
        
    def _load_state(self):
        """Load state from storage."""
        try:
            with open(self.storage_path, 'r') as f:
                self._state = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._state = {}
            
    def _save_state(self):
        """Save state to storage."""
        with open(self.storage_path, 'w') as f:
            json.dump(self._state, f)
            
    def set(self, path: str, value: Any):
        """Set state value and persist to storage."""
        super().set(path, value)
        self._save_state()

class StateManager:
    """Manages application state and provides reactive updates."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
        
    def __init__(self, ttl=3600):  # 默认1小时过期
        if not hasattr(self, 'initialized'):
            self.store = Store()
            self._state = {}
            self._listeners = {}
            self._batch_updates = False
            self._pending_updates = {}
            self._ttl = ttl
            self._timestamps = {}
            self.initialized = True
            
    def create_persistent_store(self, name: str, storage_path: str) -> PersistentStore:
        """Create a new persistent store."""
        store = PersistentStore(storage_path)
        setattr(self, f"{name}_store", store)
        return store
        
    def watch(self, paths: List[str], callback: Callable[[StateChange], None]):
        """Watch multiple paths for changes."""
        for path in paths:
            self.store.subscribe(path, callback)
            
    def unwatch(self, paths: List[str], callback: Callable[[StateChange], None]):
        """Unwatch multiple paths."""
        for path in paths:
            self.store.unsubscribe(path, callback)
            
    def set(self, key: str, value: Any):
        if self._batch_updates:
            self._pending_updates[key] = value
            return
            
        if key not in self._state or self._state[key] != value:
            self._state[key] = value
            self._timestamps[key] = time.time()
            self._notify_listeners(key)
            
    def get(self, key: str) -> Any:
        if key in self._state:
            if time.time() - self._timestamps.get(key, 0) > self._ttl:
                self._cleanup_key(key)
                return None
            return self._state[key]
        return None
        
    def _cleanup_key(self, key: str):
        self._state.pop(key, None)
        self._timestamps.pop(key, None)
        if key in self._listeners:
            del self._listeners[key]
            
    def cleanup_expired(self):
        current_time = time.time()
        expired_keys = [
            key for key, timestamp in self._timestamps.items()
            if current_time - timestamp > self._ttl
        ]
        for key in expired_keys:
            self._cleanup_key(key)
            
    @classmethod
    def get_instance(cls):
        """Get singleton instance."""
        return cls()
