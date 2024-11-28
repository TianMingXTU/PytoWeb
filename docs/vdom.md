# Virtual DOM API Reference | 虚拟 DOM API 参考

The Virtual DOM system in PytoWeb provides efficient DOM updates through diffing and patching mechanisms.
PytoWeb 的虚拟 DOM 系统通过差异和补丁机制提供高效的 DOM 更新。

## VNode | 虚拟节点

The `VNode` class represents a node in the virtual DOM tree.
`VNode` 类表示虚拟 DOM 树中的一个节点。

```python
from pytoweb.vdom import VNode

class VNode:
    def __init__(self, tag: str, props: Dict = None, children: List = None):
        self.tag = tag
        self.props = props or {}
        self.children = children or []
        self.key = props.get('key') if props else None
```

### Properties | 属性

- `tag`: HTML tag name | HTML 标签名
- `props`: Node properties/attributes | 节点属性/属性
- `children`: Child nodes | 子节点
- `key`: Unique identifier for reconciliation | 和解的唯一标识符

### Usage | 使用

```python
# Create a simple node | 创建一个简单的节点
node = VNode('div', {'class': 'container'})

# Create a node with children | 创建一个带有子节点的节点
node = VNode('div', {'class': 'container'}, [
    VNode('h1', {}, ['Hello']),
    VNode('p', {}, ['World'])
])
```

## VDOMDiffer | 虚拟 DOM 差异算法

The `VDOMDiffer` class handles the diffing process between old and new virtual DOM trees.
`VDOMDiffer` 类处理旧的和新的虚拟 DOM 树之间的差异算法。

```python
from pytoweb.vdom import VDOMDiffer

class VDOMDiffer:
    @staticmethod
    def diff(old_node: Optional[VNode], new_node: Optional[VNode]) -> List[Dict]:
        """Generate patches based on differences between nodes"""
```

### Patch Types | 补丁类型

1. **CREATE**: Create a new node | 创建一个新的节点
```python
{
    'type': 'CREATE',
    'node': new_node
}
```

2. **REMOVE**: Remove an existing node | 删除一个现有的节点
```python
{
    'type': 'REMOVE'
}
```

3. **REPLACE**: Replace an existing node | 替换一个现有的节点
```python
{
    'type': 'REPLACE',
    'node': new_node
}
```

4. **PROPS**: Update node properties | 更新节点属性
```python
{
    'type': 'PROPS',
    'props': {
        'class': 'new-class',
        'style': 'new-style'
    }
}
```

5. **CHILDREN**: Update child nodes | 更新子节点
```python
{
    'type': 'REPLACE_CHILD',
    'index': 0,
    'node': new_child
}
```

### Usage | 使用

```python
# Create old and new nodes | 创建旧的和新的节点
old_node = VNode('div', {'class': 'old'}, [VNode('p', {}, ['Old text'])])
new_node = VNode('div', {'class': 'new'}, [VNode('p', {}, ['New text'])])

# Generate patches | 生成补丁
patches = VDOMDiffer.diff(old_node, new_node)
```

## VDOMRenderer | 虚拟 DOM 渲染器

The `VDOMRenderer` class handles rendering virtual DOM nodes to HTML strings.
`VDOMRenderer` 类处理将虚拟 DOM 节点渲染为 HTML 字符串。

```python
from pytoweb.vdom import VDOMRenderer

class VDOMRenderer:
    @staticmethod
    def create_element(vnode: VNode) -> str:
        """Convert virtual node to HTML string"""
```

### Features | 特性

1. **Void Element Handling** | 空元素处理
```python
void_elements = {
    'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
    'link', 'meta', 'param', 'source', 'track', 'wbr'
}
```

2. **Property Conversion** | 属性转换
- Event handlers | 事件处理器
- Style objects | 样式对象
- Class lists | 类列表

### Usage | 使用

```python
# Create a node | 创建一个节点
node = VNode('div', {
    'class': ['container', 'main'],
    'style': {'color': 'red', 'font-size': '16px'},
    'onClick': lambda e: print('Clicked!')
})

# Render to HTML | 渲染为 HTML
html = VDOMRenderer.create_element(node)
```

## Virtual DOM | 虚拟 DOM

PytoWeb uses a Virtual DOM (VDOM) implementation to efficiently update the UI by minimizing direct manipulation of the actual DOM.

### Overview | 概述

The Virtual DOM in PytoWeb consists of three main components:

1. `VNode`: Represents a node in the virtual DOM tree
2. `VDOMDiffer`: Handles diffing between old and new virtual DOM trees
3. `VDOMRenderer`: Renders virtual DOM nodes to actual HTML

### VNode | 虚拟节点

The `VNode` class represents a node in the virtual DOM tree:

```python
from pytoweb.vdom import VNode

# Create a virtual DOM node
vnode = VNode(
    tag='div',
    props={'class': 'container', 'id': 'main'},
    children=[
        VNode('h1', {'class': 'title'}, ['Hello World']),
        VNode('p', {'class': 'content'}, ['Welcome to PytoWeb'])
    ]
)
```

### Properties | 属性

- `tag`: HTML tag name
- `props`: Dictionary of node properties (attributes)
- `children`: List of child nodes
- `key`: Optional unique identifier for optimizing list updates

### VDOMDiffer | 虚拟DOM差异处理器

The `VDOMDiffer` handles comparing and generating patches between old and new virtual DOM trees:

```python
from pytoweb.vdom import VDOMDiffer

# Generate patches
patches = VDOMDiffer.diff(old_vnode, new_vnode)
```

### Patch Types | 补丁类型

1. **CREATE**: Create a new node
```python
{
    'type': 'CREATE',
    'node': new_node
}
```

2. **REMOVE**: Remove an existing node
```python
{
    'type': 'REMOVE'
}
```

3. **REPLACE**: Replace an existing node
```python
{
    'type': 'REPLACE',
    'node': new_node
}
```

4. **PROPS**: Update node properties
```python
{
    'type': 'PROPS',
    'props': {
        'add': {'class': 'new-class'},
        'remove': ['old-prop']
    }
}
```

### VDOMRenderer | 虚拟DOM渲染器

The `VDOMRenderer` handles converting virtual DOM nodes to actual HTML:

```python
from pytoweb.vdom import VDOMRenderer

# Create renderer
renderer = VDOMRenderer()

# Render to HTML string
html = renderer.render_to_string(vnode)

# Create actual DOM element
element = renderer.create_element(vnode)
```

### String Pooling | 字符串池化

The renderer uses string pooling to optimize memory usage:

```python
# String pooling is handled automatically
renderer._pool_size = 1000  # Configure pool size
pooled_string = renderer._get_pooled_string("common string")
```

## Integration Example | 集成示例

Here's a complete example showing how the Virtual DOM system works together:
这是一个完整的示例，展示了虚拟 DOM 系统如何一起工作：

```python
from pytoweb.vdom import VNode, VDOMDiffer, VDOMRenderer

# Create initial virtual DOM | 创建初始虚拟 DOM
old_tree = VNode('div', {'class': 'container'}, [
    VNode('h1', {}, ['Hello']),
    VNode('p', {}, ['World'])
])

# Create new virtual DOM after state change | 创建状态更改后的新虚拟 DOM
new_tree = VNode('div', {'class': 'container active'}, [
    VNode('h1', {}, ['Hello']),
    VNode('p', {'style': {'color': 'red'}}, ['Updated World'])
])

# Generate patches | 生成补丁
patches = VDOMDiffer.diff(old_tree, new_tree)

# Render to HTML | 渲染为 HTML
html = VDOMRenderer.create_element(new_tree)
```

## Performance Considerations | 性能考虑

1. **Key Usage** | 键使用
```python
# Use keys for lists of elements | 为元素列表使用键
nodes = [
    VNode('li', {'key': f'item-{i}'}, [f'Item {i}'])
    for i in range(10)
]
```

2. **Memoization** | 记忆化
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def create_node(tag: str, text: str) -> VNode:
    return VNode(tag, {}, [text])
```

3. **Batch Updates** | 批量更新
```python
def update_nodes(nodes: List[VNode], updates: List[Dict]):
    # Collect all updates | 收集所有更新
    patches = []
    for node, update in zip(nodes, updates):
        patches.extend(VDOMDiffer.diff(node, update))
    
    # Apply patches in batch | 批量应用补丁
    return patches
```

## Usage in Components | 在组件中使用

Example of using Virtual DOM in a component:

```python
from pytoweb.components import Component
from pytoweb.vdom import VNode

class MyComponent(Component):
    def __init__(self):
        super().__init__()
        self.set_state('count', 0)
    
    def render(self):
        return VNode('div', {'class': 'counter'}, [
            VNode('h1', {}, [f'Count: {self.state["count"]}']),
            VNode('button', {
                'onclick': lambda e: self.set_state('count', self.state['count'] + 1)
            }, ['Increment'])
        ])
```

## Performance Optimization | 性能优化

1. **Key Property**: Use keys for list items to optimize updates
```python
items = ['A', 'B', 'C']
nodes = [VNode('li', {'key': i}, [item]) for i, item in enumerate(items)]
```

2. **Shallow Comparison**: The VDOM uses shallow comparison by default
```python
# Nodes are compared using __eq__
node1 == node2  # Compares tag, props, and children
```

3. **String Pooling**: Reuse common strings to reduce memory usage
```python
# String pooling is automatic
renderer = VDOMRenderer()
renderer._pool_size = 1000  # Adjust pool size based on needs
```
