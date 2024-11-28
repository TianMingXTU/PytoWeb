# PytoWeb Components | PytoWeb 组件

PytoWeb provides a rich set of pre-built components to help you build modern web applications quickly and efficiently.

## Basic Components | 基础组件

### Button | 按钮
```python
from pytoweb.components import Button

button = Button(text="Click me", on_click=lambda e: print("Clicked!"))
```

### Input | 输入框
```python
from pytoweb.components import Input

input = Input(
    placeholder="Enter text...",
    value="",
    on_change=lambda e: print(f"New value: {e.target.value}")
)
```

### TextArea | 文本域
```python
from pytoweb.components import TextArea

textarea = TextArea(
    value="",
    placeholder="Enter long text...",
    rows=3,
    on_change=lambda e: print(f"New value: {e.target.value}")
)
```

### Select | 选择框
```python
from pytoweb.components import Select

options = [
    {"value": "1", "label": "Option 1"},
    {"value": "2", "label": "Option 2"}
]
select = Select(options=options, on_change=lambda e: print(f"Selected: {e.target.value}"))
```

### Checkbox & Radio | 复选框和单选框
```python
from pytoweb.components import Checkbox, Radio

checkbox = Checkbox(
    label="Check me",
    checked=False,
    on_change=lambda e: print(f"Checked: {e.target.checked}")
)

radio = Radio(
    name="group1",
    value="option1",
    label="Option 1",
    checked=False,
    on_change=lambda e: print(f"Selected: {e.target.value}")
)
```

## Layout Components | 布局组件

### Container | 容器
```python
from pytoweb.components import Container

container = Container(child1, child2, child3)
```

### Grid | 网格
```python
from pytoweb.components import Grid

grid = Grid(columns=12, gap="1rem")
grid.add_item(component1, column_span=6)
grid.add_item(component2, column_span=6)
```

### Flex | 弹性布局
```python
from pytoweb.components import Flex

flex = Flex(
    direction="row",
    justify="space-between",
    align="center",
    wrap=True,
    gap="1rem"
)
```

## Navigation Components | 导航组件

### Navbar | 导航栏
```python
from pytoweb.components import Navbar

navbar = Navbar(
    brand="PytoWeb",
    items=[
        {"text": "Home", "href": "/", "active": True},
        {"text": "About", "href": "/about"}
    ],
    theme="light"
)
```

### Tabs | 选项卡
```python
from pytoweb.components import ModernTabs

tabs = ModernTabs(
    tabs=[
        {"label": "Tab 1", "content": component1},
        {"label": "Tab 2", "content": component2}
    ],
    active_index=0
)
```

## Advanced Components | 高级组件

### Modal | 模态框
```python
from pytoweb.components import ModernModal

modal = ModernModal(
    title="Modal Title",
    content="Modal Content",
    size="md",
    centered=True,
    closable=True
)
```

### Toast | 提示框
```python
from pytoweb.components import ModernToast

toast = ModernToast(
    message="Operation successful!",
    type="success",
    duration=3000,
    position="bottom-right"
)
```

### Accordion | 手风琴
```python
from pytoweb.components import ModernAccordion

accordion = ModernAccordion(
    items=[
        {"title": "Section 1", "content": content1},
        {"title": "Section 2", "content": content2}
    ],
    multiple=False
)
```

### VirtualList | 虚拟列表
```python
from pytoweb.components import VirtualList

def render_item(item):
    return Text(str(item))

virtual_list = VirtualList(
    items=large_data_list,
    render_item=render_item,
    item_height=40,
    container_height=400
)
```

### DraggableList | 可拖放列表
```python
from pytoweb.components import DraggableList

draggable_list = DraggableList(
    items=["Item 1", "Item 2", "Item 3"],
    on_reorder=lambda new_items: print("New order:", new_items)
)
```

### Table | 表格
```python
from pytoweb.components import Table

columns = [
    {"key": "id", "title": "ID"},
    {"key": "name", "title": "Name"}
]
data = [
    {"id": 1, "name": "John"},
    {"id": 2, "name": "Jane"}
]
table = Table(
    columns=columns,
    data=data,
    sortable=True,
    filterable=True,
    page_size=10
)
```

### Tree | 树形控件
```python
from pytoweb.components import Tree

tree_data = [
    {
        "id": "1",
        "label": "Node 1",
        "children": [
            {"id": "1-1", "label": "Child 1"},
            {"id": "1-2", "label": "Child 2"}
        ]
    }
]
tree = Tree(data=tree_data, expanded=False)
```

## Error Handling | 错误处理

### ErrorBoundary | 错误边界
```python
from pytoweb.components import ErrorBoundary

def fallback(error):
    return Text(f"An error occurred: {str(error)}")

error_boundary = ErrorBoundary(
    children=[component],
    fallback=fallback
)
```

### Suspense | 异步加载
```python
from pytoweb.components import Suspense, AsyncComponent

async_component = AsyncComponent()
suspense = Suspense(
    component=async_component,
    fallback=Text("Loading...")
)
