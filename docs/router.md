# PytoWeb Router System | PytoWeb 路由系统

PytoWeb provides a flexible and powerful routing system that supports path parameters, multiple HTTP methods, and named routes.

## Basic Usage | 基本用法

```python
from pytoweb.router import Router

# Create router
router = Router()

# Add route using decorator
@router.route("/hello", methods=["GET"])
def hello():
    return "Hello, World!"

# Add route using method
router.add(
    path="/users",
    handler=get_users,
    methods=["GET", "POST"]
)
```

## HTTP Method Decorators | HTTP方法装饰器

```python
# GET route
@router.get("/users")
def get_users():
    return users_list

# POST route
@router.post("/users")
def create_user():
    return create_new_user()

# PUT route
@router.put("/users/{id}")
def update_user():
    return update_user_data()

# DELETE route
@router.delete("/users/{id}")
def delete_user():
    return delete_user_data()
```

## Path Parameters | 路径参数

Routes can include dynamic path parameters:

```python
@router.get("/users/{id}")
def get_user(id: str):
    return find_user(id)

@router.get("/posts/{year}/{month}")
def get_posts(year: str, month: str):
    return find_posts(year, month)
```

## Named Routes | 命名路由

Routes can be given names for easy URL generation:

```python
@router.get("/users/{id}", name="user_detail")
def get_user(id: str):
    return find_user(id)

# Generate URL using route name
url = router.url_for("user_detail", id="123")  # "/users/123"
```

## Route Groups | 路由组

Organize related routes together:

```python
# API routes
@router.route("/api/v1/users", name="api_users")
class UserAPI:
    @router.get("")
    def list(self):
        return get_users()
        
    @router.post("")
    def create(self):
        return create_user()
        
    @router.get("/{id}")
    def detail(self, id: str):
        return get_user(id)
```

## Error Handling | 错误处理

```python
from pytoweb.router import RouterError

try:
    # Invalid path
    router.add("invalid-path", handler)  # Raises RouterError
except RouterError as e:
    print(f"Router error: {e}")

# Invalid method
@router.route("/test", methods=["INVALID"])  # Raises RouterError
def test():
    pass
```

## Route Matching | 路由匹配

The router supports different types of path matching:

```python
# Exact match
@router.get("/users")
def users():
    pass

# Parameter match
@router.get("/users/{id}")
def user(id: str):
    pass

# Custom pattern match
@router.get("/files/{filename:[^/]+\\.pdf}")
def pdf_file(filename: str):
    pass
```

## Integration with Components | 与组件集成

Use the router with PytoWeb components:

```python
from pytoweb.components import Component
from pytoweb.router import Router

router = Router()

@router.get("/")
class HomePage(Component):
    def render(self):
        return {
            "tag": "div",
            "children": ["Welcome to PytoWeb!"]
        }

@router.get("/dashboard")
class Dashboard(Component):
    def render(self):
        return {
            "tag": "div",
            "children": ["Dashboard Content"]
        }
```

## Best Practices | 最佳实践

1. Use descriptive route names
2. Group related routes together
3. Keep route handlers small and focused
4. Use path parameters for dynamic content
5. Handle errors appropriately
6. Follow RESTful conventions when applicable

## Performance Considerations | 性能考虑

1. Routes are matched in order of registration
2. Use specific routes before generic ones
3. Avoid overly complex path patterns
4. Cache frequently accessed URLs
5. Use named routes for better maintainability
