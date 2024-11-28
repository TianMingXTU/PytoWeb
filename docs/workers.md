# PytoWeb Web Workers | PytoWeb Web Workers

PytoWeb provides a Python-based web worker system for running tasks in background threads.

## Basic Usage | 基本用法

```python
from pytoweb.workers import PythonWorker

# Create a worker
worker = PythonWorker("background-tasks")

# Define message handler
def process_data(data):
    # Process data in background
    result = perform_heavy_computation(data)
    return result

# Register handler
worker.on_message("process", process_data)

# Start worker
worker.start()

# Send message to worker
worker.post_message("process", {"data": "some data"})
```

## Worker Pool | 工作池

Use WorkerPool to manage multiple workers:

```python
from pytoweb.workers import WorkerPool

# Create worker pool
pool = WorkerPool(size=4)

# Create worker
worker = pool.create_worker("background-tasks")

# Use worker as before
worker.on_message("process", process_data)
worker.start()
```

## Decorators | 装饰器

Use decorators for easy worker integration:

```python
from pytoweb.workers import WorkerDecorators

# Run function in worker
@WorkerDecorators.run_in_worker("background-tasks")
def heavy_computation(data):
    result = perform_complex_task(data)
    return result

# Register worker method
@WorkerDecorators.worker_method("process-data")
def process_data(self, data):
    return self.process(data)
```

## Message Handling | 消息处理

Handle different message types:

```python
# Multiple message handlers
worker.on_message("process", process_data)
worker.on_message("analyze", analyze_data)
worker.on_message("transform", transform_data)

# Error handling
def handle_error(error):
    logging.error(f"Worker error: {error}")

worker.on_error(handle_error)
```

## Async Communication | 异步通信

Handle asynchronous responses:

```python
# Send message with ID
worker.post_message("process", data, message_id="task-1")

# Handle response
def handle_response(message):
    if message.type == "response":
        result = message.data["result"]
        task_id = message.data["id"]
        process_result(result, task_id)

worker.on_message("response", handle_response)
```

## Component Integration | 组件集成

Use workers in components:

```python
from pytoweb.components import Component
from pytoweb.workers import PythonWorker

class DataProcessor(Component):
    def __init__(self):
        super().__init__()
        self.worker = PythonWorker("data-processor")
        self.worker.on_message("process", self.handle_result)
        self.worker.start()
        
    def process_data(self, data):
        self.worker.post_message("process", data)
        
    def handle_result(self, result):
        self.update_state({"result": result})
```

## Error Handling | 错误处理

Implement robust error handling:

```python
# Global error handler
def global_error_handler(error):
    logging.error(f"Worker error: {error}")
    notify_admin(error)

worker.on_error(global_error_handler)

# Message-specific error handling
def process_with_error_handling(data):
    try:
        result = process_data(data)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

worker.on_message("process", process_with_error_handling)
```

## Best Practices | 最佳实践

1. Worker Lifecycle
   - Start workers early in application lifecycle
   - Stop workers properly on shutdown
   - Monitor worker health

2. Message Design
   - Keep messages serializable
   - Use clear message types
   - Include message IDs for tracking

3. Error Handling
   - Implement global error handlers
   - Handle specific error cases
   - Log errors appropriately

4. Resource Management
   - Use worker pools for controlled concurrency
   - Monitor memory usage
   - Clean up resources properly

5. Performance
   - Batch related operations
   - Avoid excessive message passing
   - Monitor worker queue sizes

## Performance Considerations | 性能考虑

1. Worker Pool Size
   - Match CPU cores
   - Consider I/O vs CPU bound tasks
   - Monitor thread utilization

2. Message Queue
   - Monitor queue size
   - Implement backpressure
   - Handle queue overflow

3. Task Distribution
   - Balance load across workers
   - Group related tasks
   - Avoid worker starvation

4. Memory Management
   - Monitor memory usage
   - Clean up completed tasks
   - Avoid memory leaks

5. Communication Overhead
   - Minimize message size
   - Batch related messages
   - Use appropriate serialization
