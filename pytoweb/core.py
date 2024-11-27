"""
Core functionality for PytoWeb framework
"""

from typing import Dict, Any, Optional, Type
from .components import Component
from .vdom import VNode, VDOMRenderer, VDOMDiffer
from .events import EventBridge, StateManager
from .styles import Style
from .themes import Theme, ThemeProvider
from .animations import AnimationManager

class PytoWeb:
    """Main PytoWeb framework class"""
    
    def __init__(self):
        self.state_manager = StateManager()
        self.event_bridge = EventBridge()
        self.theme = Theme()
        ThemeProvider.set_theme(self.theme)
        
    def create_app(self, root_component: Type[Component], props: Dict[str, Any] = None) -> str:
        """Create a new PytoWeb application"""
        # Initialize root component
        instance = root_component()
        if props:
            for key, value in props.items():
                instance.set_prop(key, value)
                
        # Generate HTML
        html = self._generate_html(instance)
        
        # Add framework scripts
        html += self._get_framework_scripts()
        
        return html
        
    def _generate_html(self, root: Component) -> str:
        """Generate HTML from component tree"""
        # Get all registered animations CSS
        animations_css = AnimationManager.get_all_css()
        
        # Create HTML template
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                {animations_css}
                {self._get_default_styles()}
            </style>
        </head>
        <body>
            <div id="app">
                {root.render()}
            </div>
        </body>
        </html>
        """
        return html
        
    def _get_framework_scripts(self) -> str:
        """Get framework JavaScript code"""
        return f"""
        <script>
        {EventBridge.get_client_script()}
        
        // Framework initialization
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('PytoWeb initialized');
        }});
        </script>
        """
        
    def _get_default_styles(self) -> str:
        """Get default framework styles"""
        from .styles import DEFAULT_STYLES
        return DEFAULT_STYLES
        
    def handle_event(self, event_type: str, event_data: Dict[str, Any]):
        """Handle framework events"""
        self.event_bridge.handle_event(event_type, event_data)
        
    def set_theme(self, theme: Theme):
        """Set framework theme"""
        self.theme = theme
        ThemeProvider.set_theme(theme)
        
    def get_state_manager(self) -> StateManager:
        """Get state manager instance"""
        return self.state_manager
        
    @staticmethod
    def create_style(**styles) -> Style:
        """Create a new style instance"""
        return Style(**styles)
        
    @staticmethod
    def register_animation(name: str, keyframes: Dict[str, Dict[str, str]]):
        """Register a new animation"""
        from .animations import Animation
        animation = Animation(name, keyframes)
        AnimationManager.register(animation)
