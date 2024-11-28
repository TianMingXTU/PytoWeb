# PytoWeb Framework

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](docs/README.md)

PytoWeb是一个创新的Python Web前端框架，允许开发者使用纯Python代码构建现代化的Web应用程序。它提供了完整的组件化开发体系、虚拟DOM渲染引擎和响应式状态管理，使Python开发者能够轻松创建高性能的Web应用。

## ✨ 特性

- 🐍 纯Python开发体验
- 🔄 高效的虚拟DOM
- 📦 组件化开发
- 🎨 内置动画系统
- 🛣️ 灵活的路由
- 💾 响应式状态管理
- 🎯 表单验证
- 🎨 主题定制
- 🔧 开发者工具

## 🚀 快速开始

### 安装

```bash
pip install pytoweb
```

### 创建你的第一个应用

```python
from pytoweb import App, Component

class HelloWorld(Component):
    def render(self):
        return {
            "tag": "div",
            "children": ["Hello, PytoWeb!"]
        }

app = App()
app.mount(HelloWorld())
app.run()
```

## 📚 核心概念

### 组件系统

PytoWeb使用组件作为基本构建块。每个组件都是一个Python类，继承自`Component`基类：

```python
from pytoweb import Component

class Counter(Component):
    def __init__(self):
        super().__init__()
        self.state = {"count": 0}
    
    def increment(self):
        self.setState({"count": self.state["count"] + 1})
    
    def render(self):
        return {
            "tag": "div",
            "children": [
                {
                    "tag": "h1",
                    "children": [f"Count: {self.state['count']}"]
                },
                {
                    "tag": "button",
                    "props": {"onClick": self.increment},
                    "children": ["Increment"]
                }
            ]
        }
```

### 虚拟DOM

PytoWeb使用虚拟DOM来优化渲染性能。它会计算DOM的最小更新路径：

```python
# 虚拟DOM节点示例
vnode = {
    "tag": "div",
    "props": {"class": "container"},
    "children": [
        {
            "tag": "p",
            "children": ["Hello World"]
        }
    ]
}
```

### 状态管理

组件可以维护自己的状态，状态更新会触发重新渲染：

```python
class TodoList(Component):
    def __init__(self):
        super().__init__()
        self.state = {
            "todos": [],
            "input": ""
        }
    
    def add_todo(self):
        todos = self.state["todos"] + [self.state["input"]]
        self.setState({
            "todos": todos,
            "input": ""
        })
    
    def render(self):
        return {
            "tag": "div",
            "children": [
                {
                    "tag": "input",
                    "props": {
                        "value": self.state["input"],
                        "onChange": lambda e: self.setState({"input": e.target.value})
                    }
                },
                {
                    "tag": "button",
                    "props": {"onClick": self.add_todo},
                    "children": ["Add"]
                },
                {
                    "tag": "ul",
                    "children": [
                        {"tag": "li", "children": [todo]}
                        for todo in self.state["todos"]
                    ]
                }
            ]
        }
```

## 🎨 动画系统

PytoWeb提供了强大的动画系统：

```python
from pytoweb.animations import FadeIn

class AnimatedComponent(Component):
    def render(self):
        return {
            "tag": "div",
            "props": {"animation": FadeIn(duration=500)},
            "children": ["I will fade in!"]
        }
```

## 🛣️ 路由系统

简单的路由配置：

```python
from pytoweb import Router

router = Router([
    ("/", HomeComponent),
    ("/about", AboutComponent),
    ("/users/:id", UserComponent)
])

app = App(router=router)
app.run()
```

## 🎯 表单验证

内置的表单验证系统：

```python
from pytoweb.validation import Required, Email, MinLength

class LoginForm(Component):
    def __init__(self):
        super().__init__()
        self.validator = FormValidator()
        self.validator.add_field("email", [
            Required("Email is required"),
            Email("Invalid email format")
        ])
        self.validator.add_field("password", [
            Required("Password is required"),
            MinLength(8, "Password must be at least 8 characters")
        ])
```

## 🎨 主题系统

支持动态主题切换：

```python
from pytoweb.themes import Theme

class CustomTheme(Theme):
    colors = {
        "primary": "#007bff",
        "secondary": "#6c757d",
        "success": "#28a745"
    }
    
    typography = {
        "fontFamily": "Arial, sans-serif",
        "fontSize": "16px"
    }
```

## 📦 项目结构

```
pytoweb/
├── components/     # 基础组件
├── vdom/          # 虚拟DOM实现
├── router/        # 路由系统
├── state/         # 状态管理
├── animations/    # 动画系统
├── themes/        # 主题系统
├── validation/    # 表单验证
└── workers/       # Web Workers支持
```

## 📚 文档

详细文档请参考 [docs](docs/README.md) 目录：

- [组件系统](docs/components.md)
- [动画系统](docs/animations.md)
- [虚拟DOM](docs/vdom.md)
- [事件系统](docs/events.md)
- [路由系统](docs/router.md)
- [状态管理](docs/state.md)
- [主题系统](docs/themes.md)
- [表单验证](docs/validation.md)
- [Web Workers](docs/workers.md)

## 🤝 贡献

欢迎贡献代码！请查看[贡献指南](CONTRIBUTING.md)了解详情。

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。
