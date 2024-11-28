# PytoWeb Form Validation | PytoWeb 表单验证

PytoWeb provides a comprehensive form validation system with built-in rules and custom validation support.

## Basic Usage | 基本用法

```python
from pytoweb.validation import FormValidator, Required, Email

# Create validator
validator = FormValidator()

# Add validation rules
validator.add_field("username", [
    Required("Username is required"),
    MinLength(3, "Username must be at least 3 characters")
])

validator.add_field("email", [
    Required("Email is required"),
    Email("Please enter a valid email")
])

# Validate data
data = {
    "username": "john",
    "email": "john@example.com"
}

is_valid = validator.validate(data)
if not is_valid:
    print(validator.errors)
```

## Built-in Rules | 内置规则

### Required | 必填

```python
from pytoweb.validation import Required

# Basic required field
required = Required()

# Custom message
required = Required("This field cannot be empty")
```

### Length Validation | 长度验证

```python
from pytoweb.validation import MinLength, MaxLength

# Minimum length
min_length = MinLength(3, "Must be at least 3 characters")

# Maximum length
max_length = MaxLength(50, "Cannot exceed 50 characters")
```

### Pattern Matching | 模式匹配

```python
from pytoweb.validation import Pattern

# Custom pattern
password = Pattern(
    r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$",
    "Password must contain letters and numbers"
)
```

### Email Validation | 邮箱验证

```python
from pytoweb.validation import Email

# Basic email validation
email = Email()

# Custom message
email = Email("Please provide a valid email address")
```

### Numeric Range | 数值范围

```python
from pytoweb.validation import Range

# Value range
age = Range(18, 100, "Age must be between 18 and 100")

# Minimum only
price = Range(min_value=0, message="Price cannot be negative")

# Maximum only
quantity = Range(max_value=100, message="Maximum quantity is 100")
```

### Custom Validation | 自定义验证

```python
from pytoweb.validation import Custom

# Custom validation function
def validate_username(value):
    return value.isalnum() and len(value) >= 3

# Create custom rule
username = Custom(
    validator=validate_username,
    message="Username must be alphanumeric and at least 3 characters"
)
```

## Form Integration | 表单集成

Use validation with form components:

```python
from pytoweb.components import Form, Input
from pytoweb.validation import FormValidator, Required, Email

class ContactForm(Form):
    def __init__(self):
        super().__init__()
        
        # Create validator
        self.validator = FormValidator()
        
        # Add validation rules
        self.validator.add_field("name", [
            Required("Name is required"),
            MinLength(2, "Name is too short")
        ])
        
        self.validator.add_field("email", [
            Required("Email is required"),
            Email("Invalid email format")
        ])
        
    def on_submit(self, data):
        if self.validator.validate(data):
            # Process valid form data
            self.submit_form(data)
        else:
            # Show validation errors
            self.show_errors(self.validator.errors)
    
    def render(self):
        return {
            "tag": "form",
            "props": {"onSubmit": self.on_submit},
            "children": [
                Input(
                    name="name",
                    label="Name",
                    error=self.validator.errors.get("name")
                ),
                Input(
                    name="email",
                    label="Email",
                    error=self.validator.errors.get("email")
                )
            ]
        }
```

## Async Validation | 异步验证

Handle asynchronous validation:

```python
from pytoweb.validation import Custom
import aiohttp

async def check_username_available(username):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"/api/check-username/{username}") as response:
            return response.status == 200

# Create async validator
username_validator = Custom(
    validator=check_username_available,
    message="Username is already taken"
)
```

## Error Handling | 错误处理

Access and display validation errors:

```python
# Get all errors
all_errors = validator.errors

# Get field-specific errors
username_errors = validator.errors.get("username", [])
email_errors = validator.errors.get("email", [])

# Check if specific field has errors
has_username_errors = "username" in validator.errors
```

## Best Practices | 最佳实践

1. Use descriptive error messages
2. Combine multiple validation rules
3. Validate on both client and server
4. Handle async validation properly
5. Show errors clearly in the UI
6. Use appropriate validation rules for each field type

## Performance Considerations | 性能考虑

1. Validation rules are reusable
2. Rules are evaluated in order
3. Validation stops on first failure
4. Cache async validation results
5. Use appropriate regex patterns
