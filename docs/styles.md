# Styling System | 样式系统

PytoWeb provides a powerful and flexible styling system that allows you to style your components using Python.
PytoWeb 提供了一个强大而灵活的样式系统，允许你使用 Python 来设计组件样式。

## StyleUnit

The `StyleUnit` class represents CSS unit values.

```python
from pytoweb.styles import StyleUnit

class StyleUnit:
    def __init__(self, value: Union[int, float], unit: str = 'px'):
        self.value = value
        self.unit = unit
```

### Built-in Unit Helpers

```python
from pytoweb.styles import px, em, rem, percent, vh, vw

# Usage
width = px(100)      # "100px"
margin = em(1.5)     # "1.5em"
font_size = rem(1.2) # "1.2rem"
height = vh(100)     # "100vh"
width = vw(50)       # "50vw"
scale = percent(75)  # "75%"
```

## Style

The `Style` class is the core of the styling system.

```python
from pytoweb.styles import Style

class Style:
    def __init__(self, **styles):
        self.rules: Dict[str, str] = {}
        self.add(**styles)
```

### Methods

#### Adding Styles

```python
# Basic usage
style = Style(
    background_color='#fff',
    padding='1rem',
    border_radius='4px'
)

# Using units
style = Style(
    width=px(100),
    margin=em(1.5),
    padding=[px(10), px(20)]  # Padding shorthand
)

# Using color tuples
style = Style(
    color=(255, 0, 0),           # rgb(255, 0, 0)
    background=(0, 0, 0, 0.5)    # rgba(0, 0, 0, 0.5)
)
```

#### Modifying Styles

```python
# Add new styles
style.add(font_size=px(16), color='#000')

# Remove styles
style.remove('font_size', 'color')

# Update styles
style.update(padding=px(20), margin=em(1))

# Clone styles
new_style = style.clone()

# Merge styles
combined = style1.merge(style2)
# or
combined = style1 + style2
```

#### Converting Styles

```python
# To CSS string
css_string = style.to_string()
# Result: "background-color: #fff; padding: 1rem"

# To inline style
inline = style.inline()
# Result: 'style="background-color: #fff; padding: 1rem"'

# To dictionary
style_dict = style.to_dict()
# Result: {"background-color": "#fff", "padding": "1rem"}
```

## Predefined Styles

The `Styles` class provides commonly used style patterns.

```python
from pytoweb.styles import Styles

# Flex container
flex = Styles.flex(
    direction='row',
    justify='space-between',
    align='center',
    wrap=True
)

# Grid container
grid = Styles.grid(
    columns=12,
    gap=px(16)
)

# Card
card = Styles.card(
    shadow=True,
    radius=px(4)
)

# Button variants
button = Styles.button(variant='primary')  # or 'secondary', 'outlined'
```

## Default Styles

PytoWeb comes with a set of default styles for common components.

### Container

```css
.pytoweb-container {
    width: 100%;
    margin: 0 auto;
    padding: 0 16px;
    box-sizing: border-box;
}
```

### Grid System

```css
.pytoweb-row {
    display: flex;
    flex-wrap: wrap;
    margin: 0 -8px;
}

.pytoweb-col {
    padding: 0 8px;
    box-sizing: border-box;
}
```

### Form Elements

```css
.pytoweb-input {
    width: 100%;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    box-sizing: border-box;
}

.pytoweb-select {
    width: 100%;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    background-color: #ffffff;
    cursor: pointer;
}

.pytoweb-checkbox {
    margin-right: 8px;
}

.pytoweb-radio {
    margin-right: 8px;
}
```

### Alerts

```css
.pytoweb-alert {
    padding: 12px;
    border-radius: 4px;
    margin-bottom: 16px;
}

.pytoweb-alert-success {
    background-color: #e8f5e9;
    color: #2e7d32;
}

.pytoweb-alert-error {
    background-color: #ffebee;
    color: #c62828;
}

.pytoweb-alert-warning {
    background-color: #fff3e0;
    color: #ef6c00;
}

.pytoweb-alert-info {
    background-color: #e3f2fd;
    color: #1565c0;
}
```

## Usage Examples

### Basic Component Styling

```python
from pytoweb.components import Component
from pytoweb.styles import Style, px, em

class StyledComponent(Component):
    def __init__(self):
        super().__init__()
        self.style = Style(
            padding=px(20),
            margin=em(1),
            background_color='#fff',
            border_radius=px(4),
            box_shadow='0 2px 4px rgba(0,0,0,0.1)'
        )
```

### Responsive Design

```python
style = Style(
    width=px(100),
    padding=px(20),
    media_queries={
        '@media (min-width: 768px)': {
            'width': px(200),
            'padding': px(40)
        },
        '@media (min-width: 1024px)': {
            'width': px(300),
            'padding': px(60)
        }
    }
)
```

### Theme Integration

```python
from pytoweb.themes import Theme
from pytoweb.styles import Style

theme = Theme(
    primary_color='#007bff',
    secondary_color='#6c757d'
)

style = Style(
    background_color=theme.primary_color,
    color=theme.secondary_color
)
```

## Style Units | 样式单位

PytoWeb supports various CSS units:
PytoWeb 支持多种 CSS 单位：

```python
from pytoweb.styles import px, em, rem, percent

style = Style(
    width=px(100),      # 100px
    margin=em(1.5),     # 1.5em
    font_size=rem(1.2), # 1.2rem
    height=percent(50)  # 50%
)
```

## Responsive Design | 响应式设计

### Media Queries | 媒体查询

```python
from pytoweb.styles import MediaQuery

style = Style(
    width=px(300),
    MediaQuery('(max-width: 768px)', {
        'width': px(100),
        'padding': px(10)
    })
)
```

### Breakpoints | 断点

```python
from pytoweb.styles import Breakpoints

style = Style(
    Breakpoints.MOBILE({
        'font_size': rem(0.8)
    }),
    Breakpoints.TABLET({
        'font_size': rem(1)
    }),
    Breakpoints.DESKTOP({
        'font_size': rem(1.2)
    })
)
```

## Dynamic Styles | 动态样式

### State-based Styling | 基于状态的样式

```python
class Button(Component):
    def get_style(self):
        return Style(
            background_color='blue' if self.state['active'] else 'gray',
            color='white',
            padding=px(10),
            cursor='pointer'
        )
```

### Props-based Styling | 基于属性的样式

```python
class Card(Component):
    def __init__(self, variant='default'):
        self.variant = variant
        
    def get_style(self):
        variants = {
            'default': {'background': '#fff'},
            'primary': {'background': '#007bff'},
            'success': {'background': '#28a745'}
        }
        return Style(**variants[self.variant])
```

## Pseudo Classes | 伪类

```python
style = Style({
    '&:hover': {
        'background_color': '#f0f0f0'
    },
    '&:active': {
        'transform': 'scale(0.98)'
    }
})
```

## Animations | 动画

### Basic Animations | 基础动画

```python
from pytoweb.styles import keyframes

fade_in = keyframes({
    'from': {'opacity': 0},
    'to': {'opacity': 1}
})

style = Style(
    animation=f'{fade_in} 0.3s ease-in'
)
```

### Transition | 过渡

```python
style = Style(
    transition='all 0.3s ease-in-out',
    '&:hover': {
        'transform': 'translateY(-2px)'
    }
)
```

## Layout Utilities | 布局工具

### Flexbox | 弹性盒子

```python
flex_container = Style(
    display='flex',
    justify_content='space-between',
    align_items='center',
    flex_wrap='wrap'
)
```

### Grid | 网格

```python
grid_container = Style(
    display='grid',
    grid_template_columns='repeat(3, 1fr)',
    gap=px(20)
)
```

## Theme Integration | 主题集成

### Using Theme Variables | 使用主题变量

```python
from pytoweb.themes import useTheme

class ThemedComponent(Component):
    def render(self):
        theme = useTheme()
        return {
            'style': Style(
                color=theme.colors.primary,
                background=theme.colors.background
            )
        }
```

### Theme Variants | 主题变体

```python
style = Style({
    '.light &': {
        'background': '#fff',
        'color': '#000'
    },
    '.dark &': {
        'background': '#000',
        'color': '#fff'
    }
})
```

## Best Practices | 最佳实践

1. Use theme variables for consistency | 使用主题变量保持一致性
2. Implement responsive designs | 实现响应式设计
3. Keep styles modular and reusable | 保持样式模块化和可重用
4. Use semantic class names | 使用语义化的类名
5. Avoid inline styles when possible | 尽可能避免内联样式
