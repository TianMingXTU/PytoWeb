"""
Animation system for PytoWeb
"""

from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass
from .styles import Style

@dataclass
class AnimationTiming:
    """Animation timing configuration"""
    duration: float = 0.3
    delay: float = 0
    iteration_count: Union[int, str] = 1
    direction: str = 'normal'
    timing_function: str = 'ease'
    fill_mode: str = 'forwards'

class Animation:
    """Animation definition class"""
    
    def __init__(self, name: str, keyframes: Dict[str, Dict[str, str]], timing: Optional[AnimationTiming] = None):
        self.name = name
        self.keyframes = keyframes
        self.timing = timing or AnimationTiming()
        
    def to_css(self) -> str:
        """Convert animation to CSS"""
        css = [f'@keyframes {self.name} {{']
        
        for selector, styles in self.keyframes.items():
            css.append(f'  {selector} {{')
            for prop, value in styles.items():
                css.append(f'    {prop}: {value};')
            css.append('  }')
            
        css.append('}')
        return '\n'.join(css)
        
    def get_animation_css(self) -> str:
        """Get animation CSS properties"""
        return (
            f'animation: {self.name} '
            f'{self.timing.duration}s '
            f'{self.timing.timing_function} '
            f'{self.timing.delay}s '
            f'{self.timing.iteration_count} '
            f'{self.timing.direction} '
            f'{self.timing.fill_mode}'
        )

class AnimationSequence:
    """Animation sequence for chaining multiple animations"""
    def __init__(self, *animations: Tuple[Animation, float]):
        self.animations = animations
        self.total_duration = sum(duration for _, duration in animations)
        
    def to_css(self) -> str:
        """Convert animation sequence to CSS"""
        css_parts = []
        current_time = 0
        
        for animation, duration in self.animations:
            start_percent = (current_time / self.total_duration) * 100
            end_percent = ((current_time + duration) / self.total_duration) * 100
            
            for selector, styles in animation.keyframes.items():
                if selector == 'from':
                    selector = f'{start_percent}%'
                elif selector == 'to':
                    selector = f'{end_percent}%'
                else:
                    # 调整中间关键帧的时间点
                    original_percent = float(selector.replace('%', ''))
                    adjusted_percent = start_percent + (original_percent / 100) * (end_percent - start_percent)
                    selector = f'{adjusted_percent}%'
                
                css_parts.append(f'  {selector} {{')
                for prop, value in styles.items():
                    css_parts.append(f'    {prop}: {value};')
                css_parts.append('  }')
            
            current_time += duration
            
        return '@keyframes ' + self.name + ' {\n' + '\n'.join(css_parts) + '\n}'

class Flip(Animation):
    """3D flip animation"""
    def __init__(self, direction: str = 'x', duration: float = 0.6):
        timing = AnimationTiming(duration=duration)
        axis = 'X' if direction.lower() == 'x' else 'Y'
        
        super().__init__(f'flip-{direction}', {
            'from': {
                'transform': f'perspective(400px) rotate{axis}(0)',
                'animation-timing-function': 'ease-out'
            },
            '40%': {
                'transform': f'perspective(400px) translate{axis}(0) rotate{axis}(-20deg)',
                'animation-timing-function': 'ease-out'
            },
            '60%': {
                'transform': f'perspective(400px) rotate{axis}(10deg)',
                'animation-timing-function': 'ease-in'
            },
            '80%': {
                'transform': f'perspective(400px) rotate{axis}(-5deg)',
                'animation-timing-function': 'ease-in'
            },
            'to': {
                'transform': f'perspective(400px)',
                'animation-timing-function': 'ease-in'
            }
        }, timing)

class Elastic(Animation):
    """Elastic animation"""
    def __init__(self, direction: str = 'in', duration: float = 1.0):
        timing = AnimationTiming(duration=duration)
        
        if direction == 'in':
            keyframes = {
                '0%': {'transform': 'scale(0)'},
                '55%': {'transform': 'scale(1.05)'},
                '75%': {'transform': 'scale(0.95)'},
                '90%': {'transform': 'scale(1.02)'},
                '100%': {'transform': 'scale(1)'}
            }
        else:  # out
            keyframes = {
                '0%': {'transform': 'scale(1)'},
                '25%': {'transform': 'scale(0.95)'},
                '50%': {'transform': 'scale(1.05)'},
                '75%': {'transform': 'scale(0.95)'},
                '100%': {'transform': 'scale(0)'}
            }
            
        super().__init__(f'elastic-{direction}', keyframes, timing)

class Swing(Animation):
    """Swing animation"""
    def __init__(self, duration: float = 1.0):
        timing = AnimationTiming(duration=duration)
        super().__init__('swing', {
            '0%': {'transform': 'rotate(0deg)'},
            '20%': {'transform': 'rotate(15deg)'},
            '40%': {'transform': 'rotate(-10deg)'},
            '60%': {'transform': 'rotate(5deg)'},
            '80%': {'transform': 'rotate(-5deg)'},
            '100%': {'transform': 'rotate(0deg)'}
        }, timing)

class Wobble(Animation):
    """Wobble animation"""
    def __init__(self, duration: float = 1.0):
        timing = AnimationTiming(duration=duration)
        super().__init__('wobble', {
            '0%': {'transform': 'translateX(0%)'},
            '15%': {'transform': 'translateX(-25%) rotate(-5deg)'},
            '30%': {'transform': 'translateX(20%) rotate(3deg)'},
            '45%': {'transform': 'translateX(-15%) rotate(-3deg)'},
            '60%': {'transform': 'translateX(10%) rotate(2deg)'},
            '75%': {'transform': 'translateX(-5%) rotate(-1deg)'},
            '100%': {'transform': 'translateX(0%)'}
        }, timing)

class TypeWriter(Animation):
    """Typewriter text animation"""
    def __init__(self, text_length: int, duration: float = 2.0):
        timing = AnimationTiming(duration=duration)
        steps = {}
        
        for i in range(text_length + 1):
            percentage = (i / text_length) * 100
            steps[f'{percentage}%'] = {
                'width': f'{i}ch',
                'border-right-color': f'{"transparent" if i == text_length else "currentColor"}'
            }
            
        super().__init__('typewriter', steps, timing)

class FadeIn(Animation):
    """Fade in animation"""
    def __init__(self, duration: float = 0.3):
        timing = AnimationTiming(duration=duration)
        super().__init__('fade-in', {
            'from': {'opacity': '0'},
            'to': {'opacity': '1'}
        }, timing)

class FadeOut(Animation):
    """Fade out animation"""
    def __init__(self, duration: float = 0.3):
        timing = AnimationTiming(duration=duration)
        super().__init__('fade-out', {
            'from': {'opacity': '1'},
            'to': {'opacity': '0'}
        }, timing)

class Slide(Animation):
    """Slide animation"""
    def __init__(self, direction: str = 'left', duration: float = 0.3):
        timing = AnimationTiming(duration=duration)
        
        if direction == 'left':
            keyframes = {
                'from': {'transform': 'translateX(-100%)', 'opacity': '0'},
                'to': {'transform': 'translateX(0)', 'opacity': '1'}
            }
        elif direction == 'right':
            keyframes = {
                'from': {'transform': 'translateX(100%)', 'opacity': '0'},
                'to': {'transform': 'translateX(0)', 'opacity': '1'}
            }
        elif direction == 'up':
            keyframes = {
                'from': {'transform': 'translateY(-100%)', 'opacity': '0'},
                'to': {'transform': 'translateY(0)', 'opacity': '1'}
            }
        else:  # down
            keyframes = {
                'from': {'transform': 'translateY(100%)', 'opacity': '0'},
                'to': {'transform': 'translateY(0)', 'opacity': '1'}
            }
            
        super().__init__(f'slide-{direction}', keyframes, timing)

class Rotate(Animation):
    """Rotate animation"""
    def __init__(self, degrees: int = 360, duration: float = 0.3):
        timing = AnimationTiming(duration=duration)
        super().__init__('rotate', {
            'from': {'transform': 'rotate(0deg)'},
            'to': {'transform': f'rotate({degrees}deg)'}
        }, timing)

class Scale(Animation):
    """Scale animation"""
    def __init__(self, from_scale: float = 0, to_scale: float = 1, duration: float = 0.3):
        timing = AnimationTiming(duration=duration)
        super().__init__('scale', {
            'from': {'transform': f'scale({from_scale})'},
            'to': {'transform': f'scale({to_scale})'}
        }, timing)

class Bounce(Animation):
    """Bounce animation"""
    def __init__(self, duration: float = 1.0):
        timing = AnimationTiming(duration=duration)
        super().__init__('bounce', {
            '0%': {'transform': 'translateY(0)'},
            '20%': {'transform': 'translateY(0)'},
            '40%': {'transform': 'translateY(-30px)'},
            '50%': {'transform': 'translateY(0)'},
            '60%': {'transform': 'translateY(-15px)'},
            '80%': {'transform': 'translateY(0)'},
            '100%': {'transform': 'translateY(0)'}
        }, timing)

class Shake(Animation):
    """Shake animation"""
    def __init__(self, intensity: int = 10, duration: float = 0.8):
        timing = AnimationTiming(duration=duration)
        keyframes = {}
        steps = 10
        for i in range(steps + 1):
            percentage = f"{(i * 100) // steps}%"
            if i % 2 == 0:
                keyframes[percentage] = {'transform': f'translateX({intensity}px)'}
            else:
                keyframes[percentage] = {'transform': f'translateX(-{intensity}px)'}
        keyframes['100%'] = {'transform': 'translateX(0)'}
        
        super().__init__('shake', keyframes, timing)

class Pulse(Animation):
    """Pulse animation"""
    def __init__(self, scale: float = 1.1, duration: float = 1.0):
        timing = AnimationTiming(duration=duration, iteration_count='infinite')
        super().__init__('pulse', {
            '0%': {'transform': 'scale(1)'},
            '50%': {'transform': f'scale({scale})'},
            '100%': {'transform': 'scale(1)'}
        }, timing)

class AnimationManager:
    """Animation management class"""
    
    _animations: Dict[str, Animation] = {}
    
    @classmethod
    def register(cls, animation: Animation):
        """Register animation"""
        cls._animations[animation.name] = animation
        
    @classmethod
    def get(cls, name: str) -> Optional[Animation]:
        """Get registered animation"""
        return cls._animations.get(name)
        
    @classmethod
    def get_all_css(cls) -> str:
        """Get all animations CSS"""
        return '\n\n'.join(anim.to_css() for anim in cls._animations.values())
        
    @classmethod
    def create_sequence(cls, *animations: Tuple[str, float]) -> AnimationSequence:
        """Create animation sequence from registered animations"""
        sequence = []
        for name, delay in animations:
            animation = cls.get(name)
            if animation:
                sequence.append((animation, delay))
        return AnimationSequence(*sequence)

# 预定义动画实例
FADE_IN = FadeIn()
FADE_OUT = FadeOut()
SLIDE_IN = Slide()
SLIDE_OUT = Slide('right')
SLIDE_UP = Slide('up')
SLIDE_DOWN = Slide('down')
ROTATE = Rotate()
SCALE = Scale()
BOUNCE = Bounce()
SHAKE = Shake()
PULSE = Pulse()
ELASTIC_IN = Elastic('in')
ELASTIC_OUT = Elastic('out')
SWING = Swing()
WOBBLE = Wobble()
ZOOM_IN = Scale(0, 1, 0.3)  # 从0缩放到1
ZOOM_OUT = Scale(1, 0, 0.3)  # 从1缩放到0

# 注册预定义动画
for animation in [
    FADE_IN, FADE_OUT,
    SLIDE_IN, SLIDE_OUT, SLIDE_UP, SLIDE_DOWN,
    ROTATE, SCALE, BOUNCE, SHAKE, PULSE,
    ELASTIC_IN, ELASTIC_OUT, SWING, WOBBLE,
    ZOOM_IN, ZOOM_OUT
]:
    AnimationManager.register(animation)
