"""
Modern theme system with design tokens and variants
"""

from typing import Dict, Any

class Theme:
    """Theme management class"""
    
    def __init__(self, name: str = "default"):
        self.name = name
        self.tokens = {
            # Color System
            "colors": {
                # Brand Colors
                "primary": {
                    "main": "#1976d2",
                    "light": "#42a5f5",
                    "dark": "#1565c0",
                    "contrast": "#ffffff"
                },
                "secondary": {
                    "main": "#9c27b0",
                    "light": "#ba68c8",
                    "dark": "#7b1fa2",
                    "contrast": "#ffffff"
                },
                # Semantic Colors
                "success": {
                    "main": "#2e7d32",
                    "light": "#4caf50",
                    "dark": "#1b5e20",
                    "contrast": "#ffffff"
                },
                "warning": {
                    "main": "#ed6c02",
                    "light": "#ff9800",
                    "dark": "#e65100",
                    "contrast": "#ffffff"
                },
                "error": {
                    "main": "#d32f2f",
                    "light": "#ef5350",
                    "dark": "#c62828",
                    "contrast": "#ffffff"
                },
                "info": {
                    "main": "#0288d1",
                    "light": "#03a9f4",
                    "dark": "#01579b",
                    "contrast": "#ffffff"
                },
                # Gray Scale
                "gray": {
                    "50": "#fafafa",
                    "100": "#f5f5f5",
                    "200": "#eeeeee",
                    "300": "#e0e0e0",
                    "400": "#bdbdbd",
                    "500": "#9e9e9e",
                    "600": "#757575",
                    "700": "#616161",
                    "800": "#424242",
                    "900": "#212121"
                },
                # Background & Surface
                "background": {
                    "default": "#ffffff",
                    "paper": "#ffffff",
                    "alt": "#f8f9fa"
                },
                # Text Colors
                "text": {
                    "primary": "rgba(0, 0, 0, 0.87)",
                    "secondary": "rgba(0, 0, 0, 0.6)",
                    "disabled": "rgba(0, 0, 0, 0.38)",
                    "hint": "rgba(0, 0, 0, 0.38)"
                }
            },
            
            # Typography System
            "typography": {
                "fontFamily": {
                    "primary": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
                    "code": "'Fira Code', 'Consolas', 'Monaco', 'Andale Mono', monospace"
                },
                "fontWeight": {
                    "light": 300,
                    "regular": 400,
                    "medium": 500,
                    "semibold": 600,
                    "bold": 700
                },
                "fontSize": {
                    "xs": "0.75rem",
                    "sm": "0.875rem",
                    "base": "1rem",
                    "lg": "1.125rem",
                    "xl": "1.25rem",
                    "2xl": "1.5rem",
                    "3xl": "1.875rem",
                    "4xl": "2.25rem",
                    "5xl": "3rem"
                },
                "lineHeight": {
                    "none": 1,
                    "tight": 1.25,
                    "snug": 1.375,
                    "normal": 1.5,
                    "relaxed": 1.625,
                    "loose": 2
                },
                "letterSpacing": {
                    "tighter": "-0.05em",
                    "tight": "-0.025em",
                    "normal": "0",
                    "wide": "0.025em",
                    "wider": "0.05em",
                    "widest": "0.1em"
                }
            },
            
            # Spacing System
            "spacing": {
                "0": "0",
                "1": "0.25rem",
                "2": "0.5rem",
                "3": "0.75rem",
                "4": "1rem",
                "5": "1.25rem",
                "6": "1.5rem",
                "8": "2rem",
                "10": "2.5rem",
                "12": "3rem",
                "16": "4rem",
                "20": "5rem",
                "24": "6rem",
                "32": "8rem"
            },
            
            # Border System
            "borders": {
                "width": {
                    "none": "0",
                    "thin": "1px",
                    "medium": "2px",
                    "thick": "4px"
                },
                "radius": {
                    "none": "0",
                    "sm": "0.125rem",
                    "base": "0.25rem",
                    "md": "0.375rem",
                    "lg": "0.5rem",
                    "xl": "0.75rem",
                    "2xl": "1rem",
                    "full": "9999px"
                },
                "style": {
                    "solid": "solid",
                    "dashed": "dashed",
                    "dotted": "dotted"
                }
            },
            
            # Shadow System
            "shadows": {
                "none": "none",
                "sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
                "base": "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)",
                "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
                "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
                "xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
                "2xl": "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
                "inner": "inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)"
            },
            
            # Animation System
            "animation": {
                "duration": {
                    "fastest": "75ms",
                    "faster": "100ms",
                    "fast": "150ms",
                    "normal": "200ms",
                    "slow": "300ms",
                    "slower": "400ms",
                    "slowest": "500ms"
                },
                "easing": {
                    "linear": "linear",
                    "ease": "ease",
                    "easeIn": "cubic-bezier(0.4, 0, 1, 1)",
                    "easeOut": "cubic-bezier(0, 0, 0.2, 1)",
                    "easeInOut": "cubic-bezier(0.4, 0, 0.2, 1)"
                }
            },
            
            # Z-index System
            "zIndex": {
                "hide": -1,
                "base": 0,
                "dropdown": 1000,
                "sticky": 1100,
                "fixed": 1200,
                "modalBackdrop": 1300,
                "modal": 1400,
                "popover": 1500,
                "tooltip": 1600
            },
            
            # Breakpoints System
            "breakpoints": {
                "xs": "0px",
                "sm": "600px",
                "md": "900px",
                "lg": "1200px",
                "xl": "1536px"
            },
            
            # Grid System
            "grid": {
                "columns": 12,
                "gutter": {
                    "xs": "1rem",
                    "sm": "1.5rem",
                    "md": "2rem",
                    "lg": "2.5rem",
                    "xl": "3rem"
                },
                "margin": {
                    "xs": "1rem",
                    "sm": "1.5rem",
                    "md": "2rem",
                    "lg": "2.5rem",
                    "xl": "3rem"
                }
            }
        }
        
    def get_token(self, path: str) -> Any:
        """Get design token value by path"""
        keys = path.split(".")
        value = self.tokens
        for key in keys:
            value = value.get(key)
            if value is None:
                return None
        return value
        
    def set_token(self, path: str, value: Any):
        """Set design token value by path"""
        keys = path.split(".")
        target = self.tokens
        for key in keys[:-1]:
            target = target.setdefault(key, {})
        target[keys[-1]] = value
        
    def create_variant(self, name: str, overrides: Dict[str, Any]) -> "Theme":
        """Create theme variant with overrides"""
        variant = Theme(f"{self.name}-{name}")
        variant.tokens = self.tokens.copy()
        
        for path, value in overrides.items():
            variant.set_token(path, value)
            
        return variant
        
    @classmethod
    def create_dark_theme(cls) -> "Theme":
        """Create dark theme variant"""
        dark_theme = cls("dark")
        dark_theme.tokens["colors"].update({
            "background": {
                "default": "#121212",
                "paper": "#1e1e1e",
                "alt": "#2c2c2c"
            },
            "text": {
                "primary": "rgba(255, 255, 255, 0.87)",
                "secondary": "rgba(255, 255, 255, 0.6)",
                "disabled": "rgba(255, 255, 255, 0.38)",
                "hint": "rgba(255, 255, 255, 0.38)"
            }
        })
        return dark_theme
        
    @classmethod
    def create_high_contrast_theme(cls) -> "Theme":
        """Create high contrast theme variant"""
        high_contrast = cls("high-contrast")
        high_contrast.tokens["colors"].update({
            "background": {
                "default": "#000000",
                "paper": "#000000",
                "alt": "#1a1a1a"
            },
            "text": {
                "primary": "#ffffff",
                "secondary": "#ffffff",
                "disabled": "#808080",
                "hint": "#808080"
            }
        })
        return high_contrast

class ThemeProvider:
    """Theme provider for components"""
    
    _current_theme: Theme = None
    
    @classmethod
    def set_theme(cls, theme: Theme):
        """Set current theme"""
        cls._current_theme = theme
        
    @classmethod
    def get_theme(cls) -> Theme:
        """Get current theme"""
        return cls._current_theme
        
    @classmethod
    def use_theme(cls) -> Theme:
        """Get current theme or default"""
        if cls._current_theme is None:
            cls._current_theme = Theme({})
        return cls._current_theme
