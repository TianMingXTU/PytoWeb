"""
Core module for HTML element creation and manipulation
"""

from typing import List, Dict, Any, Optional, Callable
from .styles import Style

class Element:
    """Base class for all HTML elements"""
    
    def __init__(self, tag: str, text: str = "", **attributes):
        self.tag = tag
        self.text = text
        self.attributes = attributes
        self.children: List[Element] = []
        self.style_rules: Dict[str, str] = {}
        self.events: Dict[str, Callable] = {}
        
    def style(self, **styles) -> 'Element':
        """Add CSS styles to the element"""
        for key, value in styles.items():
            # Convert Python style names to CSS (e.g., font_size -> font-size)
            css_key = key.replace('_', '-')
            self.style_rules[css_key] = value
        return self
        
    def add(self, *children: 'Element') -> 'Element':
        """Add child elements"""
        self.children.extend(children)
        return self
        
    def on(self, event: str, handler: Callable) -> 'Element':
        """Add event handler"""
        self.events[event] = handler
        return self
        
    def render(self) -> str:
        """Render element to HTML string"""
        # Build attributes string
        attrs = self.attributes.copy()
        if self.style_rules:
            style_str = '; '.join(f'{k}: {v}' for k, v in self.style_rules.items())
            attrs['style'] = style_str
            
        # Add event handlers
        for event, handler in self.events.items():
            attrs[f'on{event}'] = f'pytoweb.handleEvent("{id(handler)}")'
            
        attrs_str = ' '.join(f'{k}="{v}"' for k, v in attrs.items())
        
        # Build HTML
        html = f'<{self.tag}'
        if attrs_str:
            html += f' {attrs_str}'
            
        if self.children or self.text:
            html += '>'
            if self.text:
                html += self.text
            for child in self.children:
                html += child.render()
            html += f'</{self.tag}>'
        else:
            html += '/>'
            
        return html
