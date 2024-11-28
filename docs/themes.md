# 主题系统 API 参考 | Theme System API Reference

PytoWeb 提供了一个强大的主题系统，允许你在应用程序中创建和管理一致的视觉风格。 | PytoWeb provides a powerful theming system that allows you to create and manage consistent visual styles across your application.

## 主题 | Theme

主题是主题系统的核心。 | The `Theme` class is the core of the theming system.

```python
from pytoweb.themes import Theme

class Theme:
    def __init__(self, **theme_values):
        self._values = {}
        self.update(theme_values)
```

### 默认主题属性 | Default Theme Properties

```python
DEFAULT_THEME = {
    # 颜色 | Colors
    'primary_color': '#007bff',
    'secondary_color': '#6c757d',
    'success_color': '#28a745',
    'danger_color': '#dc3545',
    'warning_color': '#ffc107',
    'info_color': '#17a2b8',
    'light_color': '#f8f9fa',
    'dark_color': '#343a40',
    
    # 排版 | Typography
    'font_family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial',
    'font_size_base': '1rem',
    'font_size_lg': '1.25rem',
    'font_size_sm': '0.875rem',
    'line_height_base': '1.5',
    
    # 间距 | Spacing
    'spacing_unit': '1rem',
    'spacing_xs': '0.25rem',
    'spacing_sm': '0.5rem',
    'spacing_md': '1rem',
    'spacing_lg': '1.5rem',
    'spacing_xl': '3rem',
    
    # 边框 | Borders
    'border_radius': '0.25rem',
    'border_radius_lg': '0.3rem',
    'border_radius_sm': '0.2rem',
    'border_width': '1px',
    'border_color': '#dee2e6',
    
    # 阴影 | Shadows
    'shadow_sm': '0 .125rem .25rem rgba(0,0,0,.075)',
    'shadow': '0 .5rem 1rem rgba(0,0,0,.15)',
    'shadow_lg': '0 1rem 3rem rgba(0,0,0,.175)',
    
    # 分辨率 | Breakpoints
    'breakpoint_xs': '0',
    'breakpoint_sm': '576px',
    'breakpoint_md': '768px',
    'breakpoint_lg': '992px',
    'breakpoint_xl': '1200px',
    
    # Z-index
    'zindex_dropdown': '1000',
    'zindex_sticky': '1020',
    'zindex_fixed': '1030',
    'zindex_modal_backdrop': '1040',
    'zindex_modal': '1050',
    'zindex_popover': '1060',
    'zindex_tooltip': '1070'
}
```

## 主题方法 | Theme Methods

### 创建和修改主题 | Creating and Modifying Themes

```python
# 创建新主题 | Create a new theme
theme = Theme(
    primary_color='#ff0000',
    secondary_color='#00ff00'
)

# 更新主题值 | Update theme values
theme.update({
    'font_size_base': '16px',
    'spacing_unit': '8px'
})

# 获取主题值 | Get theme value
primary_color = theme.get('primary_color')

# 检查主题是否有值 | Check if theme has value
has_color = theme.has('primary_color')
```

### 主题继承 | Theme Inheritance

```python
# 创建基主题 | Create base theme
base_theme = Theme(
    primary_color='#007bff',
    font_family='Arial'
)

# 创建派生主题 | Create derived theme
dark_theme = Theme.from_base(base_theme, {
    'primary_color': '#0056b3',
    'background_color': '#343a40'
})
```

## 主题提供者 | ThemeProvider

主题提供者负责管理应用程序中的主题。 | The `ThemeProvider` class manages theme distribution throughout the application.

```python
from pytoweb.themes import ThemeProvider

class ThemeProvider:
    def __init__(self, theme: Theme = None):
        self._theme = theme or Theme()
        self._subscribers = []
```

### 使用 | Usage

```python
# 创建主题提供者 | Create theme provider
provider = ThemeProvider(theme)

# 订阅主题更改 | Subscribe to theme changes
def theme_changed(new_theme):
    print(f"Theme updated: {new_theme}")
    
provider.subscribe(theme_changed)

# 更新主题 | Update theme
provider.set_theme(new_theme)
```

## 组件主题集成 | Component Theme Integration

组件可以使用主题提供者来获取当前主题。 | Components can use the theme provider to get the current theme.

```python
from pytoweb.components import Component
from pytoweb.themes import Theme, ThemeProvider

class ThemedButton(Component):
    def __init__(self, theme_provider: ThemeProvider):
        super().__init__()
        self.theme_provider = theme_provider
        self.theme_provider.subscribe(self.on_theme_change)
        
    def on_theme_change(self, new_theme):
        self.update_styles(new_theme)
        
    def update_styles(self, theme):
        self.style.update(
            background_color=theme.get('primary_color'),
            padding=theme.get('spacing_sm'),
            border_radius=theme.get('border_radius'),
            font_family=theme.get('font_family')
        )
```

## 主题预设 | Theme Presets

内置主题预设。 | Built-in theme presets.

```python
# 明亮主题 | Light theme
LIGHT_THEME = Theme(
    primary_color='#007bff',
    background_color='#ffffff',
    text_color='#212529'
)

# 暗黑主题 | Dark theme
DARK_THEME = Theme(
    primary_color='#0056b3',
    background_color='#343a40',
    text_color='#f8f9fa'
)

# 高对比度主题 | High contrast theme
HIGH_CONTRAST_THEME = Theme(
    primary_color='#000000',
    background_color='#ffffff',
    text_color='#000000'
)
```

## CSS 变量集成 | CSS Variable Integration

主题可以生成 CSS 变量。 | Themes can generate CSS variables.

```python
class ThemeStylesheet:
    def __init__(self, theme: Theme):
        self.theme = theme
        
    def generate_css(self) -> str:
        css = ':root {\n'
        for key, value in self.theme._values.items():
            css += f'  --{key}: {value};\n'
        css += '}\n'
        return css
        
    def apply_to_document(self):
        style_element = document.createElement('style')
        style_element.textContent = self.generate_css()
        document.head.appendChild(style_element)
```

## 动态主题切换 | Dynamic Theme Switching

主题可以动态切换。 | Themes can be dynamically switched.

```python
class ThemeSwitcher:
    def __init__(self, provider: ThemeProvider):
        self.provider = provider
        self.themes = {
            'light': LIGHT_THEME,
            'dark': DARK_THEME,
            'high-contrast': HIGH_CONTRAST_THEME
        }
        
    def switch_theme(self, theme_name: str):
        if theme_name in self.themes:
            self.provider.set_theme(self.themes[theme_name])
            
    def toggle_dark_mode(self):
        current = self.provider.get_theme()
        is_dark = current.get('background_color') == DARK_THEME.get('background_color')
        self.switch_theme('light' if is_dark else 'dark')
```

## 媒体查询集成 | Media Query Integration

主题可以使用媒体查询来实现响应式设计。 | Themes can use media queries to implement responsive design.

```python
class ResponsiveTheme(Theme):
    def __init__(self, **values):
        super().__init__(**values)
        self._media_queries = {}
        
    def add_media_query(self, query: str, theme_values: dict):
        self._media_queries[query] = theme_values
        
    def generate_css(self) -> str:
        css = super().generate_css()
        for query, values in self._media_queries.items():
            css += f'\n{query} {{\n'
            css += '  :root {\n'
            for key, value in values.items():
                css += f'    --{key}: {value};\n'
            css += '  }\n'
            css += '}\n'
        return css
```

## 主题工具 | Theme Utilities

主题工具函数。 | Theme utility functions.

```python
def lighten_color(color: str, amount: float) -> str:
    """Lighten a color by a percentage amount"""
    pass

def darken_color(color: str, amount: float) -> str:
    """Darken a color by a percentage amount"""
    pass

def create_color_palette(base_color: str) -> dict:
    """Create a color palette from a base color"""
    return {
        'lighter': lighten_color(base_color, 0.2),
        'light': lighten_color(base_color, 0.1),
        'base': base_color,
        'dark': darken_color(base_color, 0.1),
        'darker': darken_color(base_color, 0.2)
    }
```

## PytoWeb 主题系统 | PytoWeb Theme System

PytoWeb 提供了一个强大的主题系统，允许你在应用程序中创建和管理一致的视觉风格。 | PytoWeb provides a powerful theming system that allows you to create and manage consistent visual styles across your application.

### 基本用法 | Basic Usage

```python
from pytoweb.themes import Theme, ThemeProvider

# 创建主题
theme = Theme(name="custom")

# 设置为当前主题
ThemeProvider.set_theme(theme)

# 使用主题
current_theme = ThemeProvider.use_theme()
```

### 设计令牌 | Design Tokens

#### 颜色 | Colors

```python
# 品牌颜色
primary_color = theme.tokens["colors"]["primary"]["main"]      # "#1976d2"
primary_light = theme.tokens["colors"]["primary"]["light"]     # "#42a5f5"
primary_dark = theme.tokens["colors"]["primary"]["dark"]       # "#1565c0"
primary_contrast = theme.tokens["colors"]["primary"]["contrast"] # "#ffffff"

# 语义颜色
success = theme.tokens["colors"]["success"]["main"]  # "#2e7d32"
warning = theme.tokens["colors"]["warning"]["main"]  # "#ed6c02"
error = theme.tokens["colors"]["error"]["main"]      # "#d32f2f"
info = theme.tokens["colors"]["info"]["main"]        # "#0288d1"

# 灰度
gray_50 = theme.tokens["colors"]["gray"]["50"]   # "#fafafa"
gray_500 = theme.tokens["colors"]["gray"]["500"] # "#9e9e9e"
gray_900 = theme.tokens["colors"]["gray"]["900"] # "#212121"

# 背景颜色
background = theme.tokens["colors"]["background"]["default"] # "#ffffff"
paper = theme.tokens["colors"]["background"]["paper"]       # "#ffffff"
alt = theme.tokens["colors"]["background"]["alt"]          # "#f8f9fa"

# 文本颜色
text_primary = theme.tokens["colors"]["text"]["primary"]     # "rgba(0, 0, 0, 0.87)"
text_secondary = theme.tokens["colors"]["text"]["secondary"] # "rgba(0, 0, 0, 0.6)"
text_disabled = theme.tokens["colors"]["text"]["disabled"]   # "rgba(0, 0, 0, 0.38)"
```

#### 排版 | Typography

```python
# 字体家族
primary_font = theme.tokens["typography"]["fontFamily"]["primary"]
code_font = theme.tokens["typography"]["fontFamily"]["code"]

# 字体权重
light = theme.tokens["typography"]["fontWeight"]["light"]     # 300
regular = theme.tokens["typography"]["fontWeight"]["regular"] # 400
medium = theme.tokens["typography"]["fontWeight"]["medium"]   # 500
semibold = theme.tokens["typography"]["fontWeight"]["semibold"] # 600
bold = theme.tokens["typography"]["fontWeight"]["bold"]       # 700

# 字体大小
font_xs = theme.tokens["typography"]["fontSize"]["xs"]   # "0.75rem"
font_sm = theme.tokens["typography"]["fontSize"]["sm"]   # "0.875rem"
font_base = theme.tokens["typography"]["fontSize"]["base"] # "1rem"
font_xl = theme.tokens["typography"]["fontSize"]["xl"]   # "1.25rem"
font_2xl = theme.tokens["typography"]["fontSize"]["2xl"] # "1.5rem"
```

### 自定义主题 | Custom Themes

创建自定义主题：

```python
class DarkTheme(Theme):
    def __init__(self):
        super().__init__(name="dark")
        
        # 覆盖颜色
        self.tokens["colors"]["background"]["default"] = "#121212"
        self.tokens["colors"]["background"]["paper"] = "#1e1e1e"
        
        # 覆盖文本颜色
        self.tokens["colors"]["text"]["primary"] = "rgba(255, 255, 255, 0.87)"
        self.tokens["colors"]["text"]["secondary"] = "rgba(255, 255, 255, 0.6)"
        
        # 自定义令牌
        self.tokens["colors"]["custom"] = {
            "accent": "#ff4081",
            "surface": "#2c2c2c"
        }
```

### 主题提供者 | ThemeProvider

管理应用程序中的主题：

```python
# 设置主题
ThemeProvider.set_theme(DarkTheme())

# 获取当前主题
theme = ThemeProvider.get_theme()

# 使用主题（返回当前主题或默认主题）
theme = ThemeProvider.use_theme()
```

### 组件集成 | Component Integration

使用主题：

```python
from pytoweb.components import Component
from pytoweb.themes import ThemeProvider

class StyledButton(Component):
    def render(self):
        theme = ThemeProvider.use_theme()
        
        return {
            "tag": "button",
            "props": {
                "style": {
                    "backgroundColor": theme.tokens["colors"]["primary"]["main"],
                    "color": theme.tokens["colors"]["primary"]["contrast"],
                    "fontFamily": theme.tokens["typography"]["fontFamily"]["primary"],
                    "fontSize": theme.tokens["typography"]["fontSize"]["base"],
                    "fontWeight": theme.tokens["typography"]["fontWeight"]["medium"],
                    "padding": theme.tokens["spacing"]["3"],
                    "borderRadius": theme.tokens["borderRadius"]["md"]
                }
            },
            "children": ["Click Me"]
        }
```

### 响应式设计 | Responsive Design

主题支持响应式设计：

```python
# 分辨率
xs = theme.tokens["breakpoints"]["xs"]  # "0px"
sm = theme.tokens["breakpoints"]["sm"]  # "600px"
md = theme.tokens["breakpoints"]["md"]  # "900px"
lg = theme.tokens["breakpoints"]["lg"]  # "1200px"
xl = theme.tokens["breakpoints"]["xl"]  # "1536px"

# 间距
spacing = theme.tokens["spacing"]
margin = {
    "xs": spacing["2"],    # "0.5rem"
    "sm": spacing["4"],    # "1rem"
    "md": spacing["6"],    # "1.5rem"
    "lg": spacing["8"]     # "2rem"
}
```

### 最佳实践 | Best Practices

1. 使用主题令牌代替硬编码值
2. 创建语义颜色别名
3. 维护一致的间距尺度
4. 使用排版尺度进行字体大小
5. 支持暗黑模式
6. 保持主题可维护和可扩展

### 性能考虑 | Performance Considerations

1. 主题令牌被缓存
2. 主题更改触发最小的重新渲染
3. 使用浅比较进行主题更新
4. 避免主题结构中的深度嵌套
5. 通过令牌重用公共值
