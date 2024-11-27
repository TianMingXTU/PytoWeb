# Animation System | 动画系统

PytoWeb 提供了一个强大的动画系统，允许你创建流畅的交互式动画。
The PytoWeb animation system provides a powerful way to create smooth, performant animations using Python.

## Animation | 动画

The `Animation` class is the core of the animation system.
动画类是动画系统的核心。

```python
from pytoweb.animations import Animation

class Animation:
    def __init__(self, duration: int = 300, easing: str = 'ease'):
        self.duration = duration
        self.easing = easing
        self.keyframes = []
```

### Built-in Easing Functions | 内置缓动函数

```python
EASING_FUNCTIONS = {
    'linear': lambda t: t,
    'ease': lambda t: cubic_bezier(0.25, 0.1, 0.25, 1.0, t),
    'ease-in': lambda t: cubic_bezier(0.42, 0, 1.0, 1.0, t),
    'ease-out': lambda t: cubic_bezier(0, 0, 0.58, 1.0, t),
    'ease-in-out': lambda t: cubic_bezier(0.42, 0, 0.58, 1.0, t)
}
```

## Keyframe | 关键帧

The `Keyframe` class represents a single animation keyframe.
关键帧类表示单个动画关键帧。

```python
from pytoweb.animations import Keyframe

class Keyframe:
    def __init__(self, offset: float, styles: Dict[str, Any]):
        self.offset = offset  # 0.0 to 1.0
        self.styles = styles
```

### Creating Keyframes | 创建关键帧

```python
# Basic keyframe
keyframe = Keyframe(0.5, {
    'opacity': 0.5,
    'transform': 'scale(1.2)'
})

# Multiple keyframes
keyframes = [
    Keyframe(0, {'opacity': 0, 'transform': 'scale(0.8)'}),
    Keyframe(0.5, {'opacity': 0.5, 'transform': 'scale(1.1)'}),
    Keyframe(1, {'opacity': 1, 'transform': 'scale(1)'})
]
```

## AnimationBuilder | 动画构建器

The `AnimationBuilder` class provides a fluent API for creating animations.
动画构建器类提供了一个流畅的 API 用于创建动画。

```python
from pytoweb.animations import AnimationBuilder

class AnimationBuilder:
    def __init__(self):
        self.animation = Animation()
        
    def duration(self, ms: int) -> 'AnimationBuilder':
        self.animation.duration = ms
        return self
        
    def easing(self, easing: str) -> 'AnimationBuilder':
        self.animation.easing = easing
        return self
        
    def keyframe(self, offset: float, styles: Dict) -> 'AnimationBuilder':
        self.animation.keyframes.append(Keyframe(offset, styles))
        return self
        
    def build(self) -> Animation:
        return self.animation
```

### Usage | 使用方法

```python
# Create fade-in animation
fade_in = (AnimationBuilder()
    .duration(300)
    .easing('ease-in')
    .keyframe(0, {'opacity': 0})
    .keyframe(1, {'opacity': 1})
    .build())

# Create bounce animation
bounce = (AnimationBuilder()
    .duration(500)
    .easing('ease-out')
    .keyframe(0, {'transform': 'translateY(0)'})
    .keyframe(0.5, {'transform': 'translateY(-20px)'})
    .keyframe(1, {'transform': 'translateY(0)'})
    .build())
```

## Predefined Animations | 预定义动画

Common animation patterns:
常见的动画模式：

```python
# Fade animations
FADE_IN = Animation(300, 'ease-in', [
    Keyframe(0, {'opacity': 0}),
    Keyframe(1, {'opacity': 1})
])

FADE_OUT = Animation(300, 'ease-out', [
    Keyframe(0, {'opacity': 1}),
    Keyframe(1, {'opacity': 0})
])

# Scale animations
SCALE_UP = Animation(300, 'ease-out', [
    Keyframe(0, {'transform': 'scale(0)'}),
    Keyframe(1, {'transform': 'scale(1)'})
])

SCALE_DOWN = Animation(300, 'ease-in', [
    Keyframe(0, {'transform': 'scale(1)'}),
    Keyframe(1, {'transform': 'scale(0)'})
])

# Slide animations
SLIDE_IN_RIGHT = Animation(300, 'ease-out', [
    Keyframe(0, {'transform': 'translateX(100%)'}),
    Keyframe(1, {'transform': 'translateX(0)'})
])

SLIDE_OUT_LEFT = Animation(300, 'ease-in', [
    Keyframe(0, {'transform': 'translateX(0)'}),
    Keyframe(1, {'transform': 'translateX(-100%)'})
])
```

## Component Animation Integration | 组件动画集成

Example of using animations in components:
在组件中使用动画的示例：

```python
from pytoweb.components import Component
from pytoweb.animations import Animation, AnimationBuilder

class AnimatedComponent(Component):
    def __init__(self):
        super().__init__()
        self.enter_animation = (AnimationBuilder()
            .duration(300)
            .easing('ease-out')
            .keyframe(0, {'opacity': 0, 'transform': 'translateY(20px)'})
            .keyframe(1, {'opacity': 1, 'transform': 'translateY(0)'})
            .build())
            
        self.exit_animation = (AnimationBuilder()
            .duration(200)
            .easing('ease-in')
            .keyframe(0, {'opacity': 1, 'transform': 'translateY(0)'})
            .keyframe(1, {'opacity': 0, 'transform': 'translateY(-20px)'})
            .build())
            
    def on_mount(self):
        self.play_animation(self.enter_animation)
        
    def on_unmount(self):
        self.play_animation(self.exit_animation)
```

## Animation Sequence | 动画序列

The `AnimationSequence` class for creating complex animation sequences:
用于创建复杂动画序列的动画序列类：

```python
from pytoweb.animations import AnimationSequence

class AnimationSequence:
    def __init__(self):
        self.animations = []
        
    def add(self, animation: Animation, delay: int = 0):
        self.animations.append((animation, delay))
        return self
        
    def play(self):
        current_time = 0
        for animation, delay in self.animations:
            current_time += delay
            self.schedule_animation(animation, current_time)
            current_time += animation.duration
```

### Usage | 使用方法

```python
# Create animation sequence
sequence = (AnimationSequence()
    .add(FADE_IN)
    .add(SCALE_UP, delay=100)
    .add(SLIDE_IN_RIGHT, delay=200))

# Play sequence
sequence.play()
```

## Animation Groups | 动画组

The `AnimationGroup` class for parallel animations:
用于并行动画的动画组类：

```python
from pytoweb.animations import AnimationGroup

class AnimationGroup:
    def __init__(self, animations: List[Animation]):
        self.animations = animations
        
    @property
    def duration(self) -> int:
        return max(a.duration for a in self.animations)
        
    def play(self):
        for animation in self.animations:
            self.play_animation(animation)
```

### Usage | 使用方法

```python
# Create animation group
group = AnimationGroup([
    FADE_IN,
    SCALE_UP,
    SLIDE_IN_RIGHT
])

# Play animations in parallel
group.play()
```

## Performance Optimization | 性能优化

1. **GPU Acceleration**
```python
# Use transform and opacity for better performance
OPTIMIZED_ANIMATION = Animation(300, 'ease-out', [
    Keyframe(0, {
        'transform': 'translate3d(0,0,0) scale(0.8)',
        'opacity': 0
    }),
    Keyframe(1, {
        'transform': 'translate3d(0,0,0) scale(1)',
        'opacity': 1
    })
])
```

2. **Animation Recycling**
```python
class AnimationPool:
    def __init__(self, size: int = 10):
        self.pool = [Animation() for _ in range(size)]
        self.index = 0
        
    def get(self, duration: int, easing: str) -> Animation:
        animation = self.pool[self.index]
        animation.duration = duration
        animation.easing = easing
        self.index = (self.index + 1) % len(self.pool)
        return animation
```

3. **Frame Rate Control**
```python
class AnimationScheduler:
    def __init__(self, fps: int = 60):
        self.frame_duration = 1000 / fps
        self.animations = []
        
    def schedule(self, animation: Animation):
        self.animations.append(animation)
        
    def update(self, timestamp: float):
        # Update animations based on frame rate
        pass
```

```
