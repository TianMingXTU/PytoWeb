"""Web Worker support for PytoWeb."""
import json
import threading
import queue
import logging
import traceback
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

@dataclass
class WorkerMessage:
    """Message passed between main thread and worker."""
    type: str
    data: Any
    id: Optional[str] = None

class PythonWorker:
    """Python-based worker implementation."""
    
    def __init__(self, name: str):
        self.name = name
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._message_queue = queue.Queue()
        self._callbacks: Dict[str, Callable] = {}
        self._error_handler: Optional[Callable] = None
        
    def start(self):
        """Start the worker thread."""
        if self._running:
            return
            
        self._running = True
        self._thread = threading.Thread(target=self._run)
        self._thread.daemon = True
        self._thread.start()
        
    def stop(self):
        """Stop the worker thread."""
        self._running = False
        if self._thread:
            self._thread.join()
            
    def post_message(self, message_type: str, data: Any, message_id: Optional[str] = None):
        """Send a message to the worker."""
        message = WorkerMessage(type=message_type, data=data, id=message_id)
        self._message_queue.put(message)
        
    def on_message(self, message_type: str, callback: Callable):
        """Register a message handler."""
        self._callbacks[message_type] = callback
        
    def on_error(self, handler: Callable):
        """Register an error handler."""
        self._error_handler = handler
        
    def _run(self):
        """Main worker loop."""
        while self._running:
            try:
                message = self._message_queue.get(timeout=1.0)
                self._handle_message(message)
            except queue.Empty:
                continue
            except Exception as e:
                if self._error_handler:
                    self._error_handler(e)
                else:
                    logging.error(f"Worker error: {str(e)}\n{traceback.format_exc()}")
                    
    def _handle_message(self, message: WorkerMessage):
        """Handle a received message."""
        if message.type in self._callbacks:
            try:
                result = self._callbacks[message.type](message.data)
                if message.id:
                    # 如果消息有ID，发送响应
                    self.post_message('response', {
                        'id': message.id,
                        'result': result
                    })
            except Exception as e:
                if message.id:
                    # 发送错误响应
                    self.post_message('error', {
                        'id': message.id,
                        'error': str(e)
                    })
                raise

class WorkerPool:
    """Manages a pool of workers."""
    
    def __init__(self, size: int = 4):
        self._workers: Dict[str, PythonWorker] = {}
        self._executor = ThreadPoolExecutor(max_workers=size)
        self._size = size
        
    def create_worker(self, name: str) -> PythonWorker:
        """Create a new worker."""
        if name in self._workers:
            raise ValueError(f"Worker '{name}' already exists")
            
        worker = PythonWorker(name)
        self._workers[name] = worker
        worker.start()
        return worker
        
    def get_worker(self, name: str) -> Optional[PythonWorker]:
        """Get an existing worker."""
        return self._workers.get(name)
        
    def remove_worker(self, name: str):
        """Remove and stop a worker."""
        if name in self._workers:
            worker = self._workers.pop(name)
            worker.stop()
            
    def stop_all(self):
        """Stop all workers."""
        for worker in self._workers.values():
            worker.stop()
        self._workers.clear()
        self._executor.shutdown()

class WorkerDecorators:
    """Decorators for worker functionality."""
    
    @staticmethod
    def run_in_worker(worker_name: str):
        """Decorator to run a function in a worker."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                worker = WorkerPool().get_worker(worker_name)
                if not worker:
                    worker = WorkerPool().create_worker(worker_name)
                    
                # 创建消息ID
                message_id = f"{func.__name__}_{id(args)}_{id(kwargs)}"
                
                # 创建Future对象
                future = threading.Event()
                result = {'value': None, 'error': None}
                
                def handle_response(data):
                    if data['id'] == message_id:
                        if 'result' in data:
                            result['value'] = data['result']
                        else:
                            result['error'] = data['error']
                        future.set()
                        
                worker.on_message('response', handle_response)
                worker.post_message(func.__name__, {
                    'args': args,
                    'kwargs': kwargs
                }, message_id)
                
                # 等待结果
                future.wait()
                
                if result['error']:
                    raise Exception(f"Error in worker: {result['error']}")
                return result['value']
                
            return wrapper
        return decorator
        
    @staticmethod
    def worker_method(message_type: str):
        """Decorator to register a worker method."""
        def decorator(func):
            def wrapper(self, *args, **kwargs):
                if isinstance(self, PythonWorker):
                    return func(self, *args, **kwargs)
                else:
                    raise TypeError("Decorator must be used with PythonWorker class")
            
            # 注册消息处理器
            if hasattr(func, '__self__') and isinstance(func.__self__, PythonWorker):
                func.__self__.on_message(message_type, wrapper)
                
            return wrapper
        return decorator
