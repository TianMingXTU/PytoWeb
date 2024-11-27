"""Form validation system for PytoWeb"""
from typing import Dict, Any, List, Optional, Callable
import re

class ValidationRule:
    """Base class for validation rules"""
    def __init__(self, message: str):
        self.message = message
        
    def validate(self, value: Any) -> bool:
        raise NotImplementedError

class Required(ValidationRule):
    """Required field validation"""
    def __init__(self, message: str = "This field is required"):
        super().__init__(message)
        
    def validate(self, value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, str) and not value.strip():
            return False
        return True

class MinLength(ValidationRule):
    """Minimum length validation"""
    def __init__(self, min_length: int, message: str = None):
        super().__init__(message or f"Minimum length is {min_length}")
        self.min_length = min_length
        
    def validate(self, value: str) -> bool:
        return len(str(value)) >= self.min_length

class MaxLength(ValidationRule):
    """Maximum length validation"""
    def __init__(self, max_length: int, message: str = None):
        super().__init__(message or f"Maximum length is {max_length}")
        self.max_length = max_length
        
    def validate(self, value: str) -> bool:
        return len(str(value)) <= self.max_length

class Pattern(ValidationRule):
    """Pattern validation using regex"""
    def __init__(self, pattern: str, message: str = "Invalid format"):
        super().__init__(message)
        self.pattern = re.compile(pattern)
        
    def validate(self, value: str) -> bool:
        return bool(self.pattern.match(str(value)))

class Email(ValidationRule):
    """Email format validation"""
    def __init__(self, message: str = "Invalid email format"):
        super().__init__(message)
        self.pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        
    def validate(self, value: str) -> bool:
        return bool(self.pattern.match(str(value)))

class Range(ValidationRule):
    """Numeric range validation"""
    def __init__(self, min_value: float = None, max_value: float = None, message: str = None):
        message = message or f"Value must be between {min_value} and {max_value}"
        super().__init__(message)
        self.min_value = min_value
        self.max_value = max_value
        
    def validate(self, value: float) -> bool:
        try:
            num = float(value)
            if self.min_value is not None and num < self.min_value:
                return False
            if self.max_value is not None and num > self.max_value:
                return False
            return True
        except (TypeError, ValueError):
            return False

class Custom(ValidationRule):
    """Custom validation using a callback function"""
    def __init__(self, validator: Callable[[Any], bool], message: str):
        super().__init__(message)
        self.validator = validator
        
    def validate(self, value: Any) -> bool:
        return self.validator(value)

class FormValidator:
    """Form validation manager"""
    def __init__(self):
        self.fields: Dict[str, List[ValidationRule]] = {}
        self.errors: Dict[str, List[str]] = {}
        
    def add_field(self, field_name: str, rules: List[ValidationRule]):
        """Add validation rules for a field"""
        self.fields[field_name] = rules
        
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate form data"""
        self.errors.clear()
        is_valid = True
        
        for field_name, rules in self.fields.items():
            field_value = data.get(field_name)
            field_errors = []
            
            for rule in rules:
                if not rule.validate(field_value):
                    field_errors.append(rule.message)
                    is_valid = False
                    
            if field_errors:
                self.errors[field_name] = field_errors
                
        return is_valid
        
    def get_errors(self) -> Dict[str, List[str]]:
        """Get validation errors"""
        return self.errors
