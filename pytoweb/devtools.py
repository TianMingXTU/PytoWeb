"""
Development tools for PytoWeb
"""

import os
import time
import threading
import json
import psutil
import traceback
from typing import Dict, Any, List, Optional, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class PerformanceMetric:
    """Performance metric data structure."""
    component_id: str
    render_time: float
    memory_usage: int
    cpu_usage: float
    timestamp: float

class HotReloader(FileSystemEventHandler):
    """Hot reload system with enhanced features."""
    
    def __init__(self, app, watch_dirs: List[str]):
        self.app = app
        self.watch_dirs = watch_dirs
        self.observer = Observer()
        self.last_reload = 0
        self.reload_delay = 1.0
        self.file_cache = {}
        self.ignored_patterns = ['.git', '__pycache__', '*.pyc']
        
    def start(self):
        """Start watching directories with initial cache building."""
        self._build_cache()
        for directory in self.watch_dirs:
            self.observer.schedule(self, directory, recursive=True)
        self.observer.start()
        logging.info("Hot reloader started watching: %s", self.watch_dirs)
        
    def _build_cache(self):
        """Build initial file cache."""
        for directory in self.watch_dirs:
            for root, _, files in os.walk(directory):
                for file in files:
                    if not any(p in file for p in self.ignored_patterns):
                        path = os.path.join(root, file)
                        self.file_cache[path] = os.path.getmtime(path)
                        
    def stop(self):
        """Stop watching directories."""
        self.observer.stop()
        self.observer.join()
        
    def on_modified(self, event):
        """Handle file modification events with smart reload."""
        if event.is_directory:
            return
            
        if any(p in event.src_path for p in self.ignored_patterns):
            return
            
        current_time = time.time()
        if current_time - self.last_reload > self.reload_delay:
            try:
                self.last_reload = current_time
                self._smart_reload(event.src_path)
            except Exception as e:
                logging.error("Reload error: %s", str(e))
                
    def _smart_reload(self, file_path: str):
        """Smart reload system that only reloads affected components."""
        # 检查文件是否真的改变
        current_mtime = os.path.getmtime(file_path)
        if self.file_cache.get(file_path) == current_mtime:
            return
            
        self.file_cache[file_path] = current_mtime
        affected_components = self.app.get_affected_components(file_path)
        self.app.reload(affected_components)
        logging.info("Smart reloaded components: %s", affected_components)

class DebugTool:
    """Enhanced debug tool for components."""
    
    def __init__(self):
        self.components: Dict[str, Any] = {}
        self.events: List[Dict[str, Any]] = []
        self.breakpoints: Set[str] = set()
        self.logs: List[Dict[str, Any]] = []
        self.error_stack: List[Dict[str, Any]] = []
        self.state_history: List[Dict[str, Any]] = []
        
    def log_component(self, component_id: str, data: Dict[str, Any]):
        """Log component data with state tracking."""
        self.components[component_id] = data
        self.state_history.append({
            'component_id': component_id,
            'state': data.get('state'),
            'timestamp': time.time()
        })
        
    def log_event(self, event_type: str, data: Dict[str, Any]):
        """Log event data with stack trace."""
        event_data = {
            'type': event_type,
            'data': data,
            'timestamp': time.time(),
            'stack': traceback.extract_stack()
        }
        self.events.append(event_data)
        
    def log_error(self, error: Exception, component_id: Optional[str] = None):
        """Log error with detailed information."""
        error_data = {
            'type': type(error).__name__,
            'message': str(error),
            'component_id': component_id,
            'timestamp': time.time(),
            'stack': traceback.format_exc()
        }
        self.error_stack.append(error_data)
        
    def get_component_tree(self) -> Dict[str, Any]:
        """Get enhanced component hierarchy with state and props."""
        tree = {}
        for comp_id, data in self.components.items():
            if 'parent' in data:
                parent = data['parent']
                if parent not in tree:
                    tree[parent] = []
                tree[parent].append({
                    'id': comp_id,
                    'state': data.get('state'),
                    'props': data.get('props'),
                    'rendered': data.get('rendered', False)
                })
        return tree
        
    def export_debug_data(self, filepath: str):
        """Export debug data to file."""
        debug_data = {
            'components': self.components,
            'events': self.events,
            'error_stack': self.error_stack,
            'state_history': self.state_history,
            'timestamp': datetime.now().isoformat()
        }
        with open(filepath, 'w') as f:
            json.dump(debug_data, f, indent=2)

class PerformanceMonitor:
    """Enhanced performance monitoring system."""
    
    def __init__(self):
        self.metrics: List[PerformanceMetric] = []
        self.renders: Dict[str, float] = {}
        self.events: Dict[str, List[float]] = {}
        self.memory: List[Dict[str, Any]] = []
        self.process = psutil.Process()
        self.monitoring = False
        self._monitor_thread = None
        
    def start_monitoring(self, interval: float = 1.0):
        """Start continuous performance monitoring."""
        self.monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,)
        )
        self._monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join()
            
    def _monitor_loop(self, interval: float):
        """Continuous monitoring loop."""
        while self.monitoring:
            self.log_memory_usage({
                'rss': self.process.memory_info().rss,
                'vms': self.process.memory_info().vms,
                'cpu_percent': self.process.cpu_percent()
            })
            time.sleep(interval)
        
    def log_metric(self, metric: PerformanceMetric):
        """Log performance metric."""
        self.metrics.append(metric)
        
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate detailed performance report."""
        report = {
            'renders': {
                comp_id: duration
                for comp_id, duration in self.renders.items()
            },
            'events': {
                event_type: {
                    'count': len(timings),
                    'average': sum(timings) / len(timings),
                    'max': max(timings),
                    'min': min(timings)
                }
                for event_type, timings in self.events.items()
            },
            'memory': self.memory,
            'metrics': [asdict(m) for m in self.metrics],
            'summary': self._generate_summary()
        }
        return report
        
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate performance summary."""
        if not self.metrics:
            return {}
            
        return {
            'total_components': len(set(m.component_id for m in self.metrics)),
            'average_render_time': sum(m.render_time for m in self.metrics) / len(self.metrics),
            'peak_memory': max(m.memory_usage for m in self.metrics),
            'average_cpu': sum(m.cpu_usage for m in self.metrics) / len(self.metrics)
        }
        
    def export_metrics(self, filepath: str):
        """Export performance metrics to file."""
        metrics_data = {
            'metrics': [asdict(m) for m in self.metrics],
            'summary': self._generate_summary(),
            'timestamp': datetime.now().isoformat()
        }
        with open(filepath, 'w') as f:
            json.dump(metrics_data, f, indent=2)
