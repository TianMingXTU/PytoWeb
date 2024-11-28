"""
Core module for HTML element creation and manipulation
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional, Callable, Union, TypeVar, TYPE_CHECKING
from dataclasses import dataclass
from .styles import Style

T = TypeVar('T', bound='Element')

class ElementError(Exception):
    """Element creation or manipulation error"""
    pass

@dataclass
class EventHandler:
    """Event handler container"""
    name: str
    handler: Callable[..., Any]
    
    def __post_init__(self):
        if not callable(self.handler):
            raise ElementError("Event handler must be callable")

class Element:
    """Base class for all HTML elements"""
    
    VOID_ELEMENTS = {
        'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
        'link', 'meta', 'param', 'source', 'track', 'wbr'
    }
    
    def __init__(self, tag: str, text: str = "", **attributes: Any):
        """Initialize element"""
        try:
            if not isinstance(tag, str):
                raise ElementError("Tag must be a string")
            if not tag:
                raise ElementError("Tag cannot be empty")
                
            self.tag = tag.lower()  # Normalize tag name
            self.text = str(text)  # Ensure text is string
            self.attributes: Dict[str, Any] = {}
            self.children: List[Element] = []
            self.style = Style()  # Use Style class for style management
            self.events: Dict[str, EventHandler] = {}
            
            # Process attributes
            for key, value in attributes.items():
                if value is not None:  # Only add non-None attributes
                    self.attributes[key] = str(value)
                    
        except Exception as e:
            raise ElementError(f"Failed to initialize element: {e}") from e
            
    def add(self, child: Union[Element, str]) -> T:
        """Add child element"""
        try:
            if isinstance(child, str):
                child = Element('span', text=child)
            elif not isinstance(child, Element):
                raise ElementError("Child must be an Element or string")
                
            self.children.append(child)
            return self
            
        except Exception as e:
            raise ElementError(f"Failed to add child: {e}") from e
            
    def add_child(self, child: Union[Element, str]) -> T:
        """Alias for add()"""
        return self.add(child)
            
    def to_html(self) -> str:
        """Convert element to HTML string"""
        try:
            print(f"[DEBUG] Converting {self.tag} to HTML")
            # Start tag
            html = [f"<{self.tag}"]
            
            # Add attributes
            for key, value in self.attributes.items():
                html.append(f' {key}="{value}"')
                
            # Add style
            if self.style and self.style.get_all():
                style_str = '; '.join(f"{k}: {v}" for k, v in self.style.get_all().items())
                html.append(f' style="{style_str}"')
                
            # Close start tag
            html.append('>')
            
            # Add text content
            if self.text:
                html.append(self.text)
                
            # Add children
            for child in self.children:
                try:
                    child_html = child.to_html()
                    html.append(child_html)
                except Exception as e:
                    print(f"[ERROR] Failed to render child of {self.tag}: {e}")
                    raise
                    
            # Add closing tag if not void element
            if self.tag not in self.VOID_ELEMENTS:
                html.append(f"</{self.tag}>")
                
            result = ''.join(html)
            print(f"[DEBUG] Generated HTML for {self.tag}: {result[:100]}...")
            return result
            
        except Exception as e:
            print(f"[ERROR] Failed to generate HTML for {self.tag}: {e}")
            raise ElementError(f"Failed to generate HTML: {e}") from e
            
    def __str__(self) -> str:
        """String representation is HTML"""
        return self.to_html()

# Convenience functions for creating common elements
def div(*children: Element, **attrs: Any) -> Element:
    """Create a div element"""
    return Element('div', **attrs).add(*children)
    
def span(*children: Element, **attrs: Any) -> Element:
    """Create a span element"""
    return Element('span', **attrs).add(*children)
    
def p(*children: Element, **attrs: Any) -> Element:
    """Create a paragraph element"""
    return Element('p', **attrs).add(*children)
    
def a(href: str, *children: Element, **attrs: Any) -> Element:
    """Create an anchor element"""
    attrs['href'] = href
    return Element('a', **attrs).add(*children)
    
def img(src: str, alt: str = "", **attrs: Any) -> Element:
    """Create an image element"""
    attrs.update({'src': src, 'alt': alt})
    return Element('img', **attrs)
    
def button(*children: Element, **attrs: Any) -> Element:
    """Create a button element"""
    return Element('button', **attrs).add(*children)
    
def input(type: str = "text", **attrs: Any) -> Element:
    """Create an input element"""
    attrs['type'] = type
    return Element('input', **attrs)
