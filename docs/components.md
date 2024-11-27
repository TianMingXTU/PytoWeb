# Components API Reference | 组件 API 参考

## Base Component | 基础组件

The `Component` class is the foundation for all PytoWeb components. It provides core functionality for state management, props handling, and rendering.
`Component` 类是 PytoWeb 所有组件的基础。它提供了状态管理、属性处理和渲染的核心功能。

### Class: Component | 类：组件

```python
from pytoweb.components import Component

class Component:
    def __init__(self):
        self.props: Dict[str, Any] = {}
        self.state: Dict[str, Any] = {}
        self.children: List[Component] = []
        self.parent: Optional[Component] = None
        self.style = Style()
        self.tag_name = "div"  # default tag
```

#### Properties | 属性

- `props`: Dictionary of component properties | 组件属性字典
- `state`: Dictionary of component state | 组件状态字典
- `children`: List of child components | 子组件列表
- `parent`: Reference to parent component | 父组件引用
- `style`: Component's style instance | 组件样式实例
- `tag_name`: HTML tag name for the component | 组件的 HTML 标签名

#### Methods | 方法

##### State Management | 状态管理

```python
def set_state(self, key: str, value: Any) -> Component:
    """Set component state"""
    self.state[key] = value
    self._update()
    return self
```

##### Props Management | 属性管理

```python
def set_prop(self, key: str, value: Any) -> Component:
    """Set component property"""
    self.props[key] = value
    return self
```

##### Child Management | 子组件管理

```python
def add_child(self, child: Component) -> Component:
    """Add child component"""
    child.parent = self
    self.children.append(child)
    return self
```

##### Styling | 样式

```python
def apply_style(self, style: Style) -> Component:
    """Apply style to component"""
    self.style = self.style + style
    return self
```

##### Rendering | 渲染

```python
def render(self) -> str:
    """Render component to HTML string"""
    # Implementation details...
```

## Pre-built Components | 预构建组件

### Basic Components | 基础组件

#### Button | 按钮

```python
from pytoweb.components import Button

button = Button(
    text="Click me",
    on_click=lambda e: print("Clicked!")
)
```

Properties | 属性：
- `text`: Button text | 按钮文本
- `on_click`: Click event handler | 点击事件处理器

#### Input | 输入框

```python
from pytoweb.components import Input

input_field = Input(
    placeholder="Enter text",
    value="",
    on_change=lambda e: print(f"Value: {e.target.value}")
)
```

Properties | 属性：
- `placeholder`: Input placeholder text | 输入框占位符文本
- `value`: Input value | 输入框值
- `on_change`: Change event handler | 改变事件处理器

#### Form | 表单

```python
from pytoweb.components import Form

form = Form(
    on_submit=lambda e: print("Form submitted")
)
```

Properties | 属性：
- `on_submit`: Submit event handler | 提交事件处理器

#### Text | 文本

```python
from pytoweb.components import Text

text = Text(
    text="Hello, World!",
    tag="p"  # Optional HTML tag
)
```

Properties | 属性：
- `text`: Text content | 文本内容
- `tag`: HTML tag (default: "span") | HTML 标签（默认：“span”）

#### Image | 图片

```python
from pytoweb.components import Image

image = Image(
    src="/path/to/image.jpg",
    alt="Description",
    width="100px",
    height="100px"
)
```

Properties | 属性：
- `src`: Image source URL | 图片源 URL
- `alt`: Alternative text | 替代文本
- `width`: Image width | 图片宽度
- `height`: Image height | 图片高度

#### Link | 链接

```python
from pytoweb.components import Link

link = Link(
    href="/some/path",
    text="Click here",
    target="_blank"
)
```

Properties | 属性：
- `href`: Link URL | 链接 URL
- `text`: Link text | 链接文本
- `target`: Link target | 链接目标

### Layout Components | 布局组件

#### Container | 容器

```python
from pytoweb.components import Container

container = Container(
    child1,
    child2,
    child3
)
```

#### Grid | 网格

```python
from pytoweb.components import Grid

grid = Grid(
    columns=12,
    gap="1rem"
)
grid.add_item(component, column_span=6)
```

Properties | 属性：
- `columns`: Number of grid columns | 网格列数
- `gap`: Grid gap size | 网格间隙大小

#### Card | 卡片

```python
from pytoweb.components import Card

card = Card(
    title="Card Title",
    body="Card content goes here",
    footer="Card footer"
)
```

Properties | 属性：
- `title`: Card title | 卡片标题
- `body`: Card body content | 卡片正文内容
- `footer`: Card footer content | 卡片页脚内容

### Form Components | 表单组件

#### Select | 选择框

```python
from pytoweb.components import Select

select = Select(
    options=[
        {"value": "1", "label": "Option 1"},
        {"value": "2", "label": "Option 2"}
    ],
    value="1",
    on_change=lambda e: print(f"Selected: {e.target.value}")
)
```

Properties | 属性：
- `options`: List of option objects | 选项对象列表
- `value`: Selected value | 选中值
- `on_change`: Change event handler | 改变事件处理器

#### Checkbox | 复选框

```python
from pytoweb.components import Checkbox

checkbox = Checkbox(
    label="Check me",
    checked=False,
    on_change=lambda e: print(f"Checked: {e.target.checked}")
)
```

Properties | 属性：
- `label`: Checkbox label | 复选框标签
- `checked`: Checked state | 选中状态
- `on_change`: Change event handler | 改变事件处理器

#### Radio | 单选框

```python
from pytoweb.components import Radio

radio = Radio(
    name="group1",
    value="option1",
    label="Option 1",
    checked=False,
    on_change=lambda e: print(f"Selected: {e.target.value}")
)
```

Properties | 属性：
- `name`: Radio group name | 单选框组名
- `value`: Radio value | 单选框值
- `label`: Radio label | 单选框标签
- `checked`: Checked state | 选中状态
- `on_change`: Change event handler | 改变事件处理器

### Navigation Components | 导航组件

#### Navbar | 导航栏

```python
from pytoweb.components import Navbar

navbar = Navbar(
    brand="My App",
    items=[
        {"text": "Home", "href": "/"},
        {"text": "About", "href": "/about"}
    ],
    theme="light"
)
```

Properties | 属性：
- `brand`: Brand text/logo | 品牌文本/Logo
- `items`: Navigation items | 导航项
- `theme`: Navbar theme | 导航栏主题

#### Tabs | 标签页

```python
from pytoweb.components import Tabs

tabs = Tabs([
    {"label": "Tab 1", "content": "Content 1"},
    {"label": "Tab 2", "content": "Content 2"}
])
```

Properties | 属性：
- `tabs`: List of tab objects with label and content | 标签页对象列表，包含标签和内容

### Feedback Components | 反馈组件

#### Modal | 模态框

```python
from pytoweb.components import Modal

modal = Modal(
    content="Modal content",
    title="Modal Title",
    show_close=True
)
```

Properties | 属性：
- `content`: Modal content | 模态框内容
- `title`: Modal title | 模态框标题
- `show_close`: Show close button | 显示关闭按钮

#### Toast | 提示框

```python
from pytoweb.components import Toast

toast = Toast(
    message="Operation successful!",
    type="success",  # success, error, warning, info
    duration=3000
)
```

Properties | 属性：
- `message`: Toast message | 提示框消息
- `type`: Toast type | 提示框类型
- `duration`: Display duration in milliseconds | 显示时长（毫秒）

### Data Display Components | 数据显示组件

#### Table | 表格

```python
from pytoweb.components import Table

table = Table(
    columns=[
        {"key": "id", "title": "ID"},
        {"key": "name", "title": "Name"}
    ],
    data=[
        {"id": 1, "name": "John"},
        {"id": 2, "name": "Jane"}
    ],
    sortable=True,
    filterable=True,
    page_size=10
)
```

Properties | 属性：
- `columns`: Table columns configuration | 表格列配置
- `data`: Table data | 表格数据
- `sortable`: Enable sorting | 启用排序
- `filterable`: Enable filtering | 启用过滤
- `page_size`: Items per page | 每页条数

#### Tree | 树形结构

```python
from pytoweb.components import Tree

tree = Tree(
    data=[
        {
            "id": "1",
            "label": "Node 1",
            "children": [
                {"id": "1.1", "label": "Child 1"}
            ]
        }
    ],
    expanded=False
)
```

Properties | 属性：
- `data`: Tree data structure | 树形结构数据
- `expanded`: Initially expand all nodes | 初始展开所有节点

```
