# PytoWeb Animations | PytoWeb 动画

PytoWeb provides a rich set of built-in animations to enhance your web applications with smooth and engaging transitions and effects.

## Basic Usage | 基本用法

```python
from pytoweb.animations import FadeIn, FADE_IN
from pytoweb.components import Component

# Method 1: Using predefined animation instance
component.apply_animation(FADE_IN)

# Method 2: Creating custom animation instance
fade_in = FadeIn(duration=0.5)
component.apply_animation(fade_in)
```

## Built-in Animations | 内置动画

### Fade Animations | 淡入淡出动画

```python
from pytoweb.animations import FadeIn, FadeOut

# Fade In
fade_in = FadeIn(duration=0.3)  # Default duration is 0.3s

# Fade Out
fade_out = FadeOut(duration=0.3)
```

### Slide Animations | 滑动动画

```python
from pytoweb.animations import Slide

# Slide directions: 'left', 'right', 'up', 'down'
slide_left = Slide(direction='left', duration=0.3)
slide_right = Slide(direction='right', duration=0.3)
slide_up = Slide(direction='up', duration=0.3)
slide_down = Slide(direction='down', duration=0.3)
```

### Transform Animations | 变换动画

```python
from pytoweb.animations import Rotate, Scale

# Rotate
rotate = Rotate(degrees=360, duration=0.3)

# Scale
scale = Scale(from_scale=0, to_scale=1, duration=0.3)
```

### Special Effects | 特效动画

```python
from pytoweb.animations import Bounce, Shake, Pulse, Flip, Elastic, Swing, Wobble

# Bounce
bounce = Bounce(duration=1.0)

# Shake
shake = Shake(intensity=10, duration=0.8)

# Pulse
pulse = Pulse(scale=1.1, duration=1.0)

# Flip (3D)
flip_x = Flip(direction='x', duration=0.6)
flip_y = Flip(direction='y', duration=0.6)

# Elastic
elastic_in = Elastic(direction='in', duration=1.0)
elastic_out = Elastic(direction='out', duration=1.0)

# Swing
swing = Swing(duration=1.0)

# Wobble
wobble = Wobble(duration=1.0)
```

### Text Animations | 文本动画

```python
from pytoweb.animations import TypeWriter

# Typewriter effect
typewriter = TypeWriter(text_length=20, duration=2.0)
```

## Animation Timing | 动画时间设置

You can customize animation timing using the `AnimationTiming` class:

```python
from pytoweb.animations import AnimationTiming

timing = AnimationTiming(
    duration=0.3,           # Duration in seconds
    delay=0,               # Delay before start
    iteration_count=1,     # Number of iterations ('infinite' for endless)
    direction='normal',    # 'normal', 'reverse', 'alternate'
    timing_function='ease', # 'linear', 'ease', 'ease-in', 'ease-out', 'ease-in-out'
    fill_mode='forwards'   # 'none', 'forwards', 'backwards', 'both'
)
```

## Animation Manager | 动画管理器

The `AnimationManager` allows you to register, retrieve, and create sequences of animations:

```python
from pytoweb.animations import AnimationManager

# Register custom animation
AnimationManager.register(my_custom_animation)

# Get registered animation
animation = AnimationManager.get('my-animation')

# Create animation sequence
sequence = AnimationManager.create_sequence(
    ('fade-in', 0.3),
    ('slide-left', 0.5),
    ('scale', 0.3)
)
```

## Predefined Animation Instances | 预定义动画实例

PytoWeb provides several predefined animation instances for convenience:

```python
from pytoweb.animations import (
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
```

These instances can be used directly without creating new animation objects.
