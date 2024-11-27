# PytoWeb Documentation | PytoWeb 文档

PytoWeb is a modern Python web frontend framework that provides a component-based architecture with virtual DOM rendering, state management, animations, and theming capabilities.

PytoWeb 是一个现代的 Python Web 前端框架，提供基于组件的架构，包含虚拟 DOM 渲染、状态管理、动画效果和主题功能。

## Table of Contents | 目录

1. [Installation | 安装](#installation)
2. [Quick Start | 快速开始](#quick-start)
3. [Core Concepts | 核心概念](#core-concepts)
4. [Components | 组件](#components)
5. [Virtual DOM | 虚拟 DOM](#virtual-dom)
6. [Styling System | 样式系统](#styling-system)
7. [Animation System | 动画系统](#animation-system)
8. [Event Handling | 事件处理](#event-handling)
9. [State Management | 状态管理](#state-management)
10. [Theming | 主题](#theming)
11. [API Reference | API 参考](#api-reference)

## Installation | 安装

```bash
pip install pytoweb
```

## Quick Start | 快速开始

Here's a simple example to get you started:
这是一个简单的示例帮助你开始：

```python
from pytoweb import PytoWeb
from pytoweb.components import Component, Button

class HelloWorld(Component):
    def __init__(self):
        super().__init__()
        self.set_state('count', 0)
        
    def increment(self, event):
        self.set_state('count', self.state['count'] + 1)
        
    def render(self):
        return f"""
        <div>
            <h1>Hello, PytoWeb!</h1>
            <p>Count: {self.state['count']}</p>
            {Button('Increment', self.increment).render()}
        </div>
        """

app = PytoWeb()
html = app.create_app(HelloWorld)
```

## Core Concepts | 核心概念

PytoWeb is built around several core concepts:
PytoWeb 架构基于以下几个核心概念：

1. **Component-Based Architecture | 基于组件的架构**: Everything in PytoWeb is a component
   - PytoWeb 中的一切都是组件
2. **Virtual DOM | 虚拟 DOM**: Efficient rendering through virtual DOM diffing
   - 通过虚拟 DOM 差异计算实现高效渲染
3. **State Management | 状态管理**: Centralized state management with reactive updates
   - 集中式状态管理，支持响应式更新
4. **Event System | 事件系统**: Robust event handling between Python and JavaScript
   - Python 和 JavaScript 之间的健壮事件处理
5. **Styling System | 样式系统**: Flexible CSS styling with theme support
   - 灵活的 CSS 样式支持主题
6. **Animation System | 动画系统**: Rich animation capabilities
   - 丰富的动画能力

## Components | 组件

### Base Component | 基础组件

The `Component` class is the foundation of all PytoWeb components.
组件类是 PytoWeb 所有组件的基础：

- State management | 状态管理
- Props handling | 属性处理
- Lifecycle methods | 生命周期方法
- Rendering capabilities | 渲染能力

```python
from pytoweb.components import Component

class CustomComponent(Component):
    def __init__(self):
        super().__init__()
        self.tag_name = "div"  # HTML 标签
        
    def render(self):
        return "<div>Custom Component</div>"
```

### Pre-built Components | 预构建组件

PytoWeb comes with a rich set of pre-built components:
PytoWeb 提供了一系列预构建组件：

1. **Basic Components | 基础组件**
   - Button | 按钮
   - Input | 输入框
   - Form | 表单
   - Text | 文本
   - Image | 图片
   - Link | 链接

2. **Layout Components | 布局组件**
   - Container | 容器
   - Grid | 网格
   - Flex | 弹性布局
   - Card | 卡片

3. **Form Components | 表单组件**
   - Select | 选择框
   - Checkbox | 复选框
   - Radio | 单选框
   - TextArea | 文本域

4. **Navigation Components | 导航组件**
   - Navbar | 导航栏
   - Tabs | 标签页

5. **Feedback Components | 反馈组件**
   - Modal | 模态框
   - Toast | 提示框
   - Alert | 警告框

6. **Data Display Components | 数据展示组件**
   - Table | 表格
   - Tree | 树形结构
   - List | 列表

## Virtual DOM | 虚拟 DOM

PytoWeb uses a virtual DOM implementation for efficient rendering:
PytoWeb 使用虚拟 DOM 实现高效渲染：

```python
from pytoweb.vdom import VNode, VDOMRenderer

# Create virtual nodes
vnode = VNode('div', {'class': 'container'}, [
    VNode('h1', {}, ['Hello']),
    VNode('p', {}, ['World'])
])

# Render to HTML
html = VDOMRenderer.create_element(vnode)
```

## Styling System | 样式系统

### Basic Styling | 基础样式

```python
from pytoweb.styles import Style

style = Style(
    background_color='#fff',
    padding='1rem',
    border_radius='4px'
)
```

### Using Units | 使用单位

```python
from pytoweb.styles import px, em, rem

style = Style(
    width=px(100),
    margin=em(1.5),
    font_size=rem(1.2)
)
```

### Predefined Styles | 预定义样式

```python
from pytoweb.styles import Styles

flex_container = Styles.flex(
    direction='row',
    justify='space-between',
    align='center'
)

card = Styles.card(shadow=True, radius=px(8))
```

## Animation System | 动画系统

### Creating Animations | 创建动画

```python
from pytoweb.animations import Animation, AnimationTiming

fade_in = Animation('fade-in', {
    'from': {'opacity': '0'},
    'to': {'opacity': '1'}
}, AnimationTiming(duration=0.3))
```

### Using Predefined Animations | 使用预定义动画

```python
from pytoweb.animations import FadeIn, Slide, Bounce

component.apply_animation(FadeIn())
component.apply_animation(Slide('left'))
component.apply_animation(Bounce())
```

### Animation Sequences | 动画序列

```python
from pytoweb.animations import AnimationSequence

sequence = AnimationSequence(
    (FadeIn(), 0.3),
    (Slide('left'), 0.5)
)
```

## Event Handling | 事件处理

### Component Events | 组件事件

```python
class MyButton(Component):
    def handle_click(self, event):
        print('Button clicked!')
        
    def render(self):
        return Button('Click me', self.handle_click)
```

### Event Bridge | 事件桥

```python
from pytoweb.events import EventBridge

EventBridge.register_handler(lambda e: print(f"Event received: {e}"))
```

## State Management | 状态管理

### Component State | 组件状态

```python
class Counter(Component):
    def __init__(self):
        super().__init__()
        self.set_state('count', 0)
        
    def increment(self, event):
        self.set_state('count', self.state['count'] + 1)
```

### Global State | 全局状态

```python
from pytoweb.events import StateManager

state = StateManager()
state.set_state('theme', 'dark')
state.subscribe('theme', lambda value: print(f"Theme changed to: {value}"))
```

## Theming | 主题

### Creating Themes | 创建主题

```python
from pytoweb.themes import Theme

theme = Theme(
    primary_color='#007bff',
    secondary_color='#6c757d',
    font_family='Arial, sans-serif'
)
```

### Using Themes | 使用主题

```python
from pytoweb.themes import ThemeProvider

ThemeProvider.set_theme(theme)
component.apply_theme(theme)
```

## API Reference | API 参考

### PytoWeb Core | PytoWeb 核心

The main framework class that ties everything together.
框架的主要类，连接所有东西：

```python
from pytoweb import PytoWeb

app = PytoWeb()
```

Methods:
- `create_app(root_component, props)`: Create a new application
- `handle_event(event_type, event_data)`: Handle framework events
- `set_theme(theme)`: Set framework theme
- `get_state_manager()`: Get state manager instance
- `create_style(**styles)`: Create a new style instance
- `register_animation(name, keyframes)`: Register a new animation

For detailed API documentation of each module, please refer to the respective module documentation:
有关每个模块的详细 API 文档，请参阅相应模块的文档：

- [Components API | 组件 API](./components.md)
- [Virtual DOM API | 虚拟 DOM API](./vdom.md)
- [Styles API | 样式 API](./styles.md)
- [Animations API | 动画 API](./animations.md)
- [Events API | 事件 API](./events.md)
- [Themes API | 主题 API](./themes.md)
