"""
Layout system for PytoWeb
"""

from typing import List, Optional, Union, Tuple, Dict
from .components import Component, Container
from .elements import Element
from .styles import Style

class Grid(Container):
    """Grid layout component"""
    
    def __init__(self, columns: int = 12, gap: str = '1rem'):
        super().__init__()
        self.columns = columns
        self.gap = gap
        
    def render(self) -> Element:
        container = Element('div')
        container.style(
            display='grid',
            grid_template_columns=f'repeat({self.columns}, 1fr)',
            gap=self.gap
        )
        
        for child in self.children:
            container.add(child.render())
            
        return container

class Flex(Container):
    """Flexbox layout component"""
    
    def __init__(self, direction: str = 'row', justify: str = 'flex-start', 
                 align: str = 'stretch', wrap: str = 'nowrap'):
        super().__init__()
        self.direction = direction
        self.justify = justify
        self.align = align
        self.wrap = wrap
        
    def render(self) -> Element:
        container = Element('div')
        container.style(
            display='flex',
            flex_direction=self.direction,
            justify_content=self.justify,
            align_items=self.align,
            flex_wrap=self.wrap
        )
        
        for child in self.children:
            container.add(child.render())
            
        return container

class Responsive(Container):
    """Responsive layout component"""
    
    def __init__(self, breakpoints: Dict[str, str] = None):
        super().__init__()
        self.breakpoints = breakpoints or {
            'sm': '576px',
            'md': '768px',
            'lg': '992px',
            'xl': '1200px'
        }
        
    def render(self) -> Element:
        container = Element('div')
        container.style(
            width='100%',
            margin='0 auto',
            padding='0 15px'
        )
        
        # Add media queries for responsive behavior
        for size, width in self.breakpoints.items():
            container.style(**{
                f'@media (min-width: {width})': {
                    'max-width': width
                }
            })
            
        for child in self.children:
            container.add(child.render())
            
        return container
