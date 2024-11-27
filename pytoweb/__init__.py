"""
PytoWeb - Create web interfaces using pure Python

This module provides a comprehensive framework for building web interfaces using pure Python.
Version: 0.1.0
Author: PytoWeb Team
License: MIT
"""

from .app import App
from .router import Router
from .server import Server
from .components import Component, Button, Container, Text, Link, Image
from .layouts import Grid, Flex
from .themes import Theme
from .animations import (
    Animation,
    AnimationManager,
    FADE_IN,
    FADE_OUT,
    SLIDE_IN,
    SLIDE_OUT,
    SLIDE_UP,
    SLIDE_DOWN,
    ROTATE,
    SCALE,
    BOUNCE,
    SHAKE,
    PULSE,
    ELASTIC_IN,
    ELASTIC_OUT,
    SWING,
    WOBBLE,
    ZOOM_IN,
    ZOOM_OUT
)
from .events import EventBridge, EventDelegate
from .vdom import VDOMRenderer

__version__ = "0.1.0"
__author__ = "PytoWeb Team"
__license__ = "MIT"

__all__ = [
    # Core
    'App',
    'Router',
    'Server',
    'VDOMRenderer',
    
    # Components
    'Component',
    'Button',
    'Container',
    'Text',
    'Link',
    'Image',
    
    # Layouts
    'Grid',
    'Flex',
    
    # Themes
    'Theme',
    
    # Animations
    'Animation',
    'AnimationManager',
    'FADE_IN',
    'FADE_OUT',
    'SLIDE_IN',
    'SLIDE_OUT',
    'SLIDE_UP',
    'SLIDE_DOWN',
    'ROTATE',
    'SCALE',
    'BOUNCE',
    'SHAKE',
    'PULSE',
    'ELASTIC_IN',
    'ELASTIC_OUT',
    'SWING',
    'WOBBLE',
    'ZOOM_IN',
    'ZOOM_OUT',
    
    # Events
    'EventBridge',
    'EventDelegate'
]
