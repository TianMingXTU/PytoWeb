"""Error handling system for PytoWeb."""
import sys
import traceback
import logging
import json
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from datetime import datetime
from contextlib import contextmanager

@dataclass
class ErrorContext:
    """Context information for an error."""
    component: Optional[str] = None
    function: Optional[str] = None
    line_number: Optional[int] = None
    file_path: Optional[str] = None
    stack_trace: Optional[str] = None
    additional_info: Dict[str, Any] = None

@dataclass
class ErrorReport:
    """Detailed error report."""
    error_type: str
    message: str
    context: ErrorContext
    timestamp: datetime
    severity: str
    handled: bool

class ErrorBoundary:
    """Error boundary for components."""
    
    def __init__(self, fallback_component=None):
        self.fallback_component = fallback_component
        self.has_error = False
        self.error: Optional[Exception] = None
        self.error_info: Optional[ErrorContext] = None
        
    @contextmanager
    def catch(self):
        """Context manager for catching errors."""
        try:
            yield
        except Exception as e:
            self.has_error = True
            self.error = e
            self.error_info = ErrorContext(
                stack_trace=traceback.format_exc(),
                additional_info={
                    'time': datetime.now().isoformat()
                }
            )
            ErrorHandler.get_instance().handle_error(e, self.error_info)
            
    def render(self):
        """Render component or fallback."""
        if self.has_error and self.fallback_component:
            return self.fallback_component
        return None

class ErrorHandler:
    """Central error handling system."""
    
    _instance = None
    
    def __init__(self):
        self.error_listeners: List[Callable[[ErrorReport], None]] = []
        self.error_history: List[ErrorReport] = []
        self.max_history = 100
        self.logger = logging.getLogger('pytoweb.errors')
        
    @classmethod
    def get_instance(cls):
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    def add_listener(self, listener: Callable[[ErrorReport], None]):
        """Add error listener."""
        self.error_listeners.append(listener)
        
    def remove_listener(self, listener: Callable[[ErrorReport], None]):
        """Remove error listener."""
        self.error_listeners.remove(listener)
        
    def handle_error(self, error: Exception, context: Optional[ErrorContext] = None):
        """Handle an error."""
        # 创建错误报告
        report = ErrorReport(
            error_type=type(error).__name__,
            message=str(error),
            context=context or self._get_error_context(),
            timestamp=datetime.now(),
            severity=self._get_error_severity(error),
            handled=False
        )
        
        # 记录错误
        self.error_history.append(report)
        if len(self.error_history) > self.max_history:
            self.error_history.pop(0)
            
        # 通知监听器
        for listener in self.error_listeners:
            try:
                listener(report)
            except Exception as e:
                self.logger.error(f"Error in error listener: {e}")
                
        # 记录到日志
        self.logger.error(
            f"Error: {report.error_type}: {report.message}",
            extra={
                'context': context.__dict__ if context else None,
                'timestamp': report.timestamp.isoformat()
            }
        )
        
    def _get_error_context(self) -> ErrorContext:
        """Get context from current exception."""
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if not exc_traceback:
            return ErrorContext()
            
        # 获取最后一个堆栈帧
        tb = traceback.extract_tb(exc_traceback)[-1]
        return ErrorContext(
            function=tb.name,
            line_number=tb.lineno,
            file_path=tb.filename,
            stack_trace=traceback.format_exc()
        )
        
    def _get_error_severity(self, error: Exception) -> str:
        """Determine error severity."""
        if isinstance(error, (SystemError, MemoryError)):
            return 'CRITICAL'
        if isinstance(error, (ValueError, TypeError)):
            return 'ERROR'
        if isinstance(error, Warning):
            return 'WARNING'
        return 'ERROR'
        
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of recent errors."""
        return {
            'total_errors': len(self.error_history),
            'error_types': self._count_error_types(),
            'recent_errors': [
                {
                    'type': e.error_type,
                    'message': e.message,
                    'timestamp': e.timestamp.isoformat(),
                    'severity': e.severity
                }
                for e in self.error_history[-10:]
            ]
        }
        
    def _count_error_types(self) -> Dict[str, int]:
        """Count occurrences of each error type."""
        counts = {}
        for error in self.error_history:
            counts[error.error_type] = counts.get(error.error_type, 0) + 1
        return counts
        
    def export_error_report(self, filepath: str):
        """Export error history to file."""
        report = {
            'errors': [
                {
                    'type': e.error_type,
                    'message': e.message,
                    'context': e.context.__dict__,
                    'timestamp': e.timestamp.isoformat(),
                    'severity': e.severity,
                    'handled': e.handled
                }
                for e in self.error_history
            ],
            'summary': self.get_error_summary()
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)

def error_boundary(fallback_component=None):
    """Decorator to create an error boundary."""
    def decorator(component_class):
        original_render = component_class.render
        
        def wrapped_render(self, *args, **kwargs):
            boundary = ErrorBoundary(fallback_component)
            with boundary.catch():
                return original_render(self, *args, **kwargs)
            return boundary.render()
            
        component_class.render = wrapped_render
        return component_class
    return decorator
