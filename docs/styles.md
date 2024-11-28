# PytoWeb Styling System | PytoWeb 样式系统

PytoWeb provides a powerful and flexible styling system that supports modern CSS features, including glass morphism, neumorphism, gradients, and responsive design.

## Basic Usage | 基本用法

```python
from pytoweb.styles import Style, px, rem, em

# Create a style
style = Style(
    width=px(200),
    height=px(100),
    margin=rem(1),
    padding=em(1.5),
    background_color="#ffffff",
    border_radius=px(4)
)
```

## Style Units | 样式单位

PytoWeb provides helper functions for common CSS units:

```python
from pytoweb.styles import px, em, rem, percent, vh, vw

# Available units
width = px(100)      # pixels
margin = em(1.5)     # em units
padding = rem(2)     # root em units
height = percent(50) # percentage
min_height = vh(100) # viewport height
max_width = vw(100)  # viewport width
```

## Modern Style Features | 现代样式特性

### Glass Morphism | 玻璃态效果

```python
from pytoweb.styles import ModernStyle

style = ModernStyle()
style.add_glass_effect(opacity=0.1)
```

### Neumorphism | 新拟态

```python
style = ModernStyle()
style.add_neumorphism(
    color="#ffffff",
    type="flat"  # or "pressed"
)
```

### Gradients | 渐变

```python
from pytoweb.styles import StyleSystem

# Linear gradient
gradient = StyleSystem.create_gradient(
    start_color="#ff0000",
    end_color="#00ff00",
    direction="to right"
)

# Text gradient
text_gradient = StyleSystem.create_text_gradient(
    start_color="#ff0000",
    end_color="#00ff00"
)
```

### Animations & Transitions | 动画和过渡

```python
# Add animation
style.add_animation(
    keyframes={
        "0%": {"opacity": "0"},
        "100%": {"opacity": "1"}
    },
    duration="0.3s",
    timing="ease"
)

# Add transition
style.add_transition(
    properties=["opacity", "transform"],
    duration="0.3s",
    timing="ease"
)
```

### Responsive Design | 响应式设计

```python
style = ModernStyle()
style.add_responsive(
    breakpoint="768px",
    styles={
        "flex_direction": "column",
        "padding": px(16)
    }
)
```

## Style Presets | 样式预设

PytoWeb includes common style presets for rapid development:

### Button Styles | 按钮样式

```python
from pytoweb.styles import StylePresets

# Button variants
primary_button = StylePresets.button(variant="primary", size="md")
secondary_button = StylePresets.button(variant="secondary", size="lg")
```

### Card Styles | 卡片样式

```python
# Card with elevation
card = StylePresets.card(elevation="md")
```

### Input Styles | 输入框样式

```python
# Input variants
outline_input = StylePresets.input(variant="outline")
filled_input = StylePresets.input(variant="filled")
```

### Badge Styles | 徽章样式

```python
# Badge variants
badge = StylePresets.badge(variant="primary")
```

## Layout Helpers | 布局助手

PytoWeb provides predefined layout styles:

### Flex Layout | 弹性布局

```python
from pytoweb.styles import Styles

flex_container = Styles.flex(
    direction="row",
    justify="space-between",
    align="center",
    wrap=True
)
```

### Grid Layout | 网格布局

```python
grid_container = Styles.grid(
    columns=12,
    gap=px(16)
)
```

## Interactive States | 交互状态

ModernStyle supports interactive state styling:

```python
style = ModernStyle()

# Hover effect
style.add_hover({
    "background_color": "#f0f0f0",
    "transform": "scale(1.05)"
})

# Focus effect
style.add_focus({
    "border_color": "#0066cc",
    "box_shadow": "0 0 0 2px rgba(0,102,204,0.2)"
})

# Active effect
style.add_active({
    "transform": "scale(0.98)"
})
```

## Default Styles | 默认样式

PytoWeb includes a set of default styles for common components:

```python
from pytoweb.styles import DEFAULT_STYLES

# Default styles are automatically applied to PytoWeb components
# You can override them by adding your own styles
```

These default styles provide a modern, clean look while maintaining good usability and accessibility.
