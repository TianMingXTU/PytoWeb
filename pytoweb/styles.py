"""
Modern styling system with advanced features
"""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass

@dataclass
class StyleUnit:
    """CSS unit value"""
    value: Union[int, float]
    unit: str = 'px'
    
    def __str__(self) -> str:
        return f"{self.value}{self.unit}"

class Style:
    """CSS style management class"""
    
    def __init__(self, **styles):
        self.rules: Dict[str, str] = {}
        self.add(**styles)
        
    def add(self, **styles) -> 'Style':
        """Add CSS styles"""
        for key, value in styles.items():
            # Convert Python style names to CSS (e.g., font_size -> font-size)
            css_key = key.replace('_', '-')
            
            # Handle StyleUnit objects
            if isinstance(value, StyleUnit):
                value = str(value)
            # Handle color tuples (RGB or RGBA)
            elif isinstance(value, tuple):
                if len(value) == 3:
                    value = f"rgb({value[0]}, {value[1]}, {value[2]})"
                elif len(value) == 4:
                    value = f"rgba({value[0]}, {value[1]}, {value[2]}, {value[3]})"
            # Handle lists (e.g., for multiple background images)
            elif isinstance(value, list):
                value = ', '.join(str(v) for v in value)
                
            self.rules[css_key] = str(value)
        return self
        
    def remove(self, *keys) -> 'Style':
        """Remove CSS styles"""
        for key in keys:
            css_key = key.replace('_', '-')
            self.rules.pop(css_key, None)
        return self
        
    def get(self, key: str) -> str:
        """Get style value"""
        css_key = key.replace('_', '-')
        return self.rules.get(css_key, '')
        
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary"""
        return self.rules.copy()
        
    def to_string(self) -> str:
        """Convert to CSS string"""
        return '; '.join(f'{k}: {v}' for k, v in self.rules.items())
        
    def to_class_string(self) -> str:
        """Convert to CSS class definition"""
        return ' '.join(self.rules.keys())
        
    def inline(self) -> str:
        """Convert to inline style string"""
        return self.to_string()
        
    def update(self, **styles) -> 'Style':
        """Update CSS styles"""
        return self.add(**styles)
        
    def merge(self, other: 'Style') -> 'Style':
        """Merge with another style"""
        new_style = Style()
        new_style.rules.update(self.rules)
        new_style.rules.update(other.rules)
        return new_style
        
    def clone(self) -> 'Style':
        """Create a copy of this style"""
        new_style = Style()
        new_style.rules.update(self.rules)
        return new_style
        
    def __getattr__(self, name: str) -> str:
        """Get style value using attribute access"""
        return self.get(name)
        
    def __add__(self, other: 'Style') -> 'Style':
        """Combine two styles"""
        return self.merge(other)
        
    def __str__(self) -> str:
        """Convert to string"""
        return self.to_string()

class StyleSystem:
    """Modern styling system with advanced features"""
    
    @staticmethod
    def create_gradient(start_color: str, end_color: str, direction: str = "to right") -> str:
        """Create linear gradient"""
        return f"linear-gradient({direction}, {start_color}, {end_color})"
        
    @staticmethod
    def create_glass_effect(opacity: float = 0.1) -> Dict[str, str]:
        """Create glass morphism effect"""
        return {
            "background": f"rgba(255, 255, 255, {opacity})",
            "backdrop_filter": "blur(10px)",
            "border": "1px solid rgba(255, 255, 255, 0.2)",
            "box_shadow": "0 8px 32px 0 rgba(31, 38, 135, 0.37)"
        }
        
    @staticmethod
    def create_neumorphism(color: str, type: str = "flat") -> Dict[str, str]:
        """Create neumorphism effect"""
        if type == "pressed":
            return {
                "background": color,
                "box_shadow": f"inset 5px 5px 10px rgba(0, 0, 0, 0.1), inset -5px -5px 10px rgba(255, 255, 255, 0.1)"
            }
        else:
            return {
                "background": color,
                "box_shadow": "5px 5px 10px rgba(0, 0, 0, 0.1), -5px -5px 10px rgba(255, 255, 255, 0.1)"
            }
            
    @staticmethod
    def create_text_gradient(start_color: str, end_color: str) -> Dict[str, str]:
        """Create text gradient effect"""
        return {
            "background": f"linear-gradient(to right, {start_color}, {end_color})",
            "background_clip": "text",
            "text_fill_color": "transparent",
            "-webkit-background-clip": "text",
            "-webkit-text-fill-color": "transparent"
        }
        
    @staticmethod
    def create_animation(keyframes: Dict[str, Dict[str, str]], duration: str = "0.3s", timing: str = "ease") -> Dict[str, str]:
        """Create CSS animation"""
        animation_name = f"animation_{hash(str(keyframes))}"
        keyframe_rules = []
        
        for selector, styles in keyframes.items():
            style_rules = [f"{k}: {v}" for k, v in styles.items()]
            keyframe_rules.append(f"{selector} {{ {'; '.join(style_rules)} }}")
            
        keyframe_css = f"@keyframes {animation_name} {{ {' '.join(keyframe_rules)} }}"
        
        # TODO: Add keyframe CSS to global styles
        
        return {
            "animation": f"{animation_name} {duration} {timing}"
        }
        
    @staticmethod
    def create_transition(properties: List[str], duration: str = "0.3s", timing: str = "ease") -> str:
        """Create CSS transition"""
        return ", ".join([f"{prop} {duration} {timing}" for prop in properties])
        
    @staticmethod
    def create_media_query(breakpoint: str, styles: Dict[str, str]) -> str:
        """Create media query"""
        return f"@media (min-width: {breakpoint}) {{ {'; '.join([f'{k}: {v}' for k, v in styles.items()])} }}"
        
    @staticmethod
    def create_hover_effect(styles: Dict[str, str]) -> Dict[str, str]:
        """Create hover effect styles"""
        return {f"&:hover": styles}
        
    @staticmethod
    def create_focus_effect(styles: Dict[str, str]) -> Dict[str, str]:
        """Create focus effect styles"""
        return {f"&:focus": styles}
        
    @staticmethod
    def create_active_effect(styles: Dict[str, str]) -> Dict[str, str]:
        """Create active effect styles"""
        return {f"&:active": styles}

class ModernStyle(Style):
    """Enhanced style class with modern features"""
    
    def add_glass_effect(self, opacity: float = 0.1):
        """Add glass morphism effect"""
        self.add(**StyleSystem.create_glass_effect(opacity))
        return self
        
    def add_neumorphism(self, color: str, type: str = "flat"):
        """Add neumorphism effect"""
        self.add(**StyleSystem.create_neumorphism(color, type))
        return self
        
    def add_text_gradient(self, start_color: str, end_color: str):
        """Add text gradient effect"""
        self.add(**StyleSystem.create_text_gradient(start_color, end_color))
        return self
        
    def add_animation(self, keyframes: Dict[str, Dict[str, str]], duration: str = "0.3s", timing: str = "ease"):
        """Add CSS animation"""
        self.add(**StyleSystem.create_animation(keyframes, duration, timing))
        return self
        
    def add_transition(self, properties: List[str], duration: str = "0.3s", timing: str = "ease"):
        """Add CSS transition"""
        self.add(transition=StyleSystem.create_transition(properties, duration, timing))
        return self
        
    def add_hover(self, styles: Dict[str, str]):
        """Add hover effect"""
        self.add(**StyleSystem.create_hover_effect(styles))
        return self
        
    def add_focus(self, styles: Dict[str, str]):
        """Add focus effect"""
        self.add(**StyleSystem.create_focus_effect(styles))
        return self
        
    def add_active(self, styles: Dict[str, str]):
        """Add active effect"""
        self.add(**StyleSystem.create_active_effect(styles))
        return self
        
    def add_responsive(self, breakpoint: str, styles: Dict[str, str]):
        """Add responsive styles"""
        self.add_raw(StyleSystem.create_media_query(breakpoint, styles))
        return self

class StylePresets:
    """Predefined modern style presets"""
    
    @staticmethod
    def button(variant: str = "primary", size: str = "md") -> Dict[str, str]:
        """Button style preset"""
        base_styles = {
            "border": "none",
            "border_radius": "0.375rem",
            "font_weight": "500",
            "cursor": "pointer",
            "transition": "all 0.2s ease-in-out"
        }
        
        # Size variants
        sizes = {
            "sm": {"padding": "0.5rem 1rem", "font_size": "0.875rem"},
            "md": {"padding": "0.75rem 1.5rem", "font_size": "1rem"},
            "lg": {"padding": "1rem 2rem", "font_size": "1.125rem"}
        }
        
        # Color variants
        variants = {
            "primary": {
                "background": "#3b82f6",
                "color": "#ffffff",
                "&:hover": {"background": "#2563eb"},
                "&:active": {"background": "#1d4ed8"}
            },
            "secondary": {
                "background": "#6b7280",
                "color": "#ffffff",
                "&:hover": {"background": "#4b5563"},
                "&:active": {"background": "#374151"}
            },
            "outline": {
                "background": "transparent",
                "border": "2px solid #3b82f6",
                "color": "#3b82f6",
                "&:hover": {"background": "#3b82f6", "color": "#ffffff"},
                "&:active": {"background": "#2563eb", "color": "#ffffff"}
            },
            "ghost": {
                "background": "transparent",
                "color": "#3b82f6",
                "&:hover": {"background": "rgba(59, 130, 246, 0.1)"},
                "&:active": {"background": "rgba(59, 130, 246, 0.2)"}
            }
        }
        
        return {**base_styles, **sizes[size], **variants[variant]}
        
    @staticmethod
    def card(elevation: str = "md") -> Dict[str, str]:
        """Card style preset"""
        base_styles = {
            "background": "#ffffff",
            "border_radius": "0.5rem",
            "padding": "1.5rem",
            "transition": "all 0.2s ease-in-out"
        }
        
        elevations = {
            "sm": {"box_shadow": "0 1px 2px 0 rgba(0, 0, 0, 0.05)"},
            "md": {"box_shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.1)"},
            "lg": {"box_shadow": "0 10px 15px -3px rgba(0, 0, 0, 0.1)"}
        }
        
        return {**base_styles, **elevations[elevation]}
        
    @staticmethod
    def input(variant: str = "outline") -> Dict[str, str]:
        """Input style preset"""
        base_styles = {
            "padding": "0.75rem 1rem",
            "font_size": "1rem",
            "border_radius": "0.375rem",
            "transition": "all 0.2s ease-in-out",
            "&:focus": {
                "outline": "none",
                "ring": "2px",
                "ring_color": "rgba(59, 130, 246, 0.5)"
            }
        }
        
        variants = {
            "outline": {
                "border": "1px solid #d1d5db",
                "background": "#ffffff",
                "&:hover": {"border_color": "#9ca3af"},
                "&:focus": {"border_color": "#3b82f6"}
            },
            "filled": {
                "border": "1px solid transparent",
                "background": "#f3f4f6",
                "&:hover": {"background": "#e5e7eb"},
                "&:focus": {"background": "#ffffff", "border_color": "#3b82f6"}
            },
            "flushed": {
                "border": "none",
                "border_bottom": "1px solid #d1d5db",
                "border_radius": "0",
                "&:hover": {"border_bottom_color": "#9ca3af"},
                "&:focus": {"border_bottom_color": "#3b82f6"}
            }
        }
        
        return {**base_styles, **variants[variant]}
        
    @staticmethod
    def badge(variant: str = "primary") -> Dict[str, str]:
        """Badge style preset"""
        base_styles = {
            "display": "inline-flex",
            "align_items": "center",
            "padding": "0.25rem 0.75rem",
            "font_size": "0.875rem",
            "font_weight": "500",
            "border_radius": "9999px",
            "line_height": "1"
        }
        
        variants = {
            "primary": {
                "background": "#e0f2fe",
                "color": "#0369a1"
            },
            "success": {
                "background": "#dcfce7",
                "color": "#15803d"
            },
            "warning": {
                "background": "#fef3c7",
                "color": "#b45309"
            },
            "error": {
                "background": "#fee2e2",
                "color": "#b91c1c"
            }
        }
        
        return {**base_styles, **variants[variant]}

# Helper functions for creating style units
def px(value: Union[int, float]) -> StyleUnit:
    """Create pixel unit"""
    return StyleUnit(value, 'px')

def em(value: Union[int, float]) -> StyleUnit:
    """Create em unit"""
    return StyleUnit(value, 'em')

def rem(value: Union[int, float]) -> StyleUnit:
    """Create rem unit"""
    return StyleUnit(value, 'rem')

def percent(value: Union[int, float]) -> StyleUnit:
    """Create percentage unit"""
    return StyleUnit(value, '%')

def vh(value: Union[int, float]) -> StyleUnit:
    """Create viewport height unit"""
    return StyleUnit(value, 'vh')

def vw(value: Union[int, float]) -> StyleUnit:
    """Create viewport width unit"""
    return StyleUnit(value, 'vw')

# Predefined styles
class Styles:
    """Predefined styles collection"""
    
    @staticmethod
    def flex(direction: str = 'row', justify: str = 'flex-start', align: str = 'stretch',
             wrap: bool = False) -> Style:
        """Create flex container style"""
        return Style(
            display='flex',
            flex_direction=direction,
            justify_content=justify,
            align_items=align,
            flex_wrap='wrap' if wrap else 'nowrap'
        )
    
    @staticmethod
    def grid(columns: int = 12, gap: Union[str, StyleUnit] = px(16)) -> Style:
        """Create grid container style"""
        return Style(
            display='grid',
            grid_template_columns=f'repeat({columns}, 1fr)',
            gap=str(gap)
        )
    
    @staticmethod
    def card(shadow: bool = True, radius: Union[str, StyleUnit] = px(4)) -> Style:
        """Create card style"""
        style = Style(
            padding=px(16),
            border_radius=str(radius),
            background_color='#ffffff'
        )
        if shadow:
            style.add(box_shadow='0 2px 4px rgba(0,0,0,0.1)')
        return style
    
    @staticmethod
    def button(variant: str = 'primary') -> Style:
        """Create button style"""
        base_style = Style(
            padding=f'{px(8)} {px(16)}',
            border_radius=px(4),
            border='none',
            cursor='pointer',
            font_weight='500',
            transition='all 0.2s ease'
        )
        
        variants = {
            'primary': Style(
                background_color='#1976d2',
                color='#ffffff',
                hover={'background_color': '#1565c0'}
            ),
            'secondary': Style(
                background_color='#9e9e9e',
                color='#ffffff',
                hover={'background_color': '#757575'}
            ),
            'outlined': Style(
                background_color='transparent',
                color='#1976d2',
                border='1px solid #1976d2',
                hover={'background_color': 'rgba(25,118,210,0.04)'}
            )
        }
        
        return base_style + variants.get(variant, variants['primary'])

# Default styles
DEFAULT_STYLES = """
.pytoweb-container {
    width: 100%;
    margin: 0 auto;
    padding: 0 16px;
    box-sizing: border-box;
}

.pytoweb-row {
    display: flex;
    flex-wrap: wrap;
    margin: 0 -8px;
}

.pytoweb-col {
    padding: 0 8px;
    box-sizing: border-box;
}

.pytoweb-card {
    background: #ffffff;
    border-radius: 4px;
    padding: 16px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.pytoweb-button {
    display: inline-block;
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 500;
    text-align: center;
    transition: all 0.2s ease;
}

.pytoweb-button:hover {
    opacity: 0.9;
}

.pytoweb-input {
    width: 100%;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    box-sizing: border-box;
}

.pytoweb-input:focus {
    outline: none;
    border-color: #1976d2;
}

.pytoweb-label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
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

.pytoweb-textarea {
    width: 100%;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    min-height: 100px;
    resize: vertical;
}

.pytoweb-form {
    width: 100%;
}

.pytoweb-form-group {
    margin-bottom: 16px;
}

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
"""
