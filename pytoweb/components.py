"""
PytoWeb组件系统

提供基础和高级UI组件，支持虚拟滚动、拖放等功能。
"""

from __future__ import annotations
from typing import (
    Dict, Any, Optional, Callable, List, Set,
    TypeVar, TypedDict, Union
)
from collections import OrderedDict
import weakref
import logging
from .elements import Element
from .styles import Style
from .events import EventDelegate, Event

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 类型别名
T = TypeVar('T')
OptionsType = List[Dict[str, str]]
EventHandler = Callable[..., None]
ComponentList = List['Component']
PropDict = Dict[str, Any]
StateDict = Dict[str, Any]

class ComponentCache:
    """组件缓存系统"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
        
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self._cache: OrderedDict[str, Any] = OrderedDict()
            self._max_size = 100
            self._logger = logging.getLogger(__name__)
            self.initialized = True
            
    def get(self, key: str) -> Optional[Any]:
        """获取缓存的组件"""
        try:
            if key in self._cache:
                value = self._cache.pop(key)
                self._cache[key] = value
                return value
        except Exception as e:
            self._logger.error(f"Error getting cached component: {e}", exc_info=True)
        return None
        
    def set(self, key: str, value: Any):
        """缓存组件"""
        try:
            if key in self._cache:
                self._cache.pop(key)
            elif len(self._cache) >= self._max_size:
                self._cache.popitem(last=False)
            self._cache[key] = value
        except Exception as e:
            self._logger.error(f"Error caching component: {e}", exc_info=True)
            
    def clear(self):
        """清除缓存"""
        self._cache.clear()

class Component:
    """所有组件的基类"""
    
    def __init__(self):
        self.props: PropDict = {}
        self.state: StateDict = {}
        self.children: ComponentList = []
        self.parent: Optional['Component'] = None
        self.style = Style()
        self.tag_name = "div"  # 默认标签
        self._cache = ComponentCache()
        self._logger = logging.getLogger(__name__)
        
        # 添加基本事件委托
        self.on_mount = EventDelegate()
        self.on_unmount = EventDelegate()
        self.on_update = EventDelegate()
        self.on_error = EventDelegate()

    def mount(self):
        """组件挂载时调用"""
        try:
            self.on_mount(self)
        except Exception as e:
            self._logger.error(f"Error mounting component: {e}", exc_info=True)
            self.on_error(e)
            
    def unmount(self):
        """组件卸载时调用"""
        try:
            self.on_unmount(self)
        except Exception as e:
            self._logger.error(f"Error unmounting component: {e}", exc_info=True)
            self.on_error(e)
            
    def update(self):
        """组件更新时调用"""
        try:
            self._update()  # 调用原有的_update方法
            self.on_update(self)
        except Exception as e:
            self._logger.error(f"Error updating component: {e}", exc_info=True)
            self.on_error(e)
            
    def set_prop(self, key: str, value: Any) -> 'Component':
        """设置组件属性"""
        try:
            self.props[key] = value
            return self
        except Exception as e:
            self._logger.error(f"Error setting prop {key}: {e}", exc_info=True)
            raise
        
    def set_state(self, key: str, value: Any) -> 'Component':
        """设置组件状态"""
        try:
            if self.state.get(key) != value:
                self.state[key] = value
                self._update()
            return self
        except Exception as e:
            self._logger.error(f"Error setting state {key}: {e}", exc_info=True)
            raise
        
    def add_child(self, child: 'Component') -> 'Component':
        """添加子组件"""
        try:
            child.parent = self
            self.children.append(child)
            return self
        except Exception as e:
            self._logger.error(f"Error adding child component: {e}", exc_info=True)
            raise
        
    def apply_style(self, style: Style) -> 'Component':
        """应用样式"""
        try:
            self.style = self.style + style
            return self
        except Exception as e:
            self._logger.error(f"Error applying style: {e}", exc_info=True)
            raise
        
    def _update(self):
        """更新组件状态"""
        try:
            # 触发重新渲染
            cache_key = f"{self.__class__.__name__}_{id(self)}"
            self._cache.clear()  # 清除该组件的缓存
            self._logger.debug(f"Component {cache_key} updated")
        except Exception as e:
            self._logger.error(f"Error updating component: {e}", exc_info=True)
        
    def __getattr__(self, name: str) -> Any:
        """通过属性访问获取组件属性"""
        if name in self.props:
            return self.props[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        
    def render(self) -> Element:
        """渲染组件"""
        try:
            cache_key = f"{self.__class__.__name__}_{id(self)}"
            cached = self._cache.get(cache_key)
            if cached:
                return cached
                
            element = Element(self.tag_name)
            element.style = self.style
            
            # 渲染子组件
            for child in self.children:
                element.append_child(child.render())
                
            self._cache.set(cache_key, element)
            return element
            
        except Exception as e:
            self._logger.error(f"Error rendering component: {e}", exc_info=True)
            raise

class Button(Component):
    """预构建的Button组件"""
    
    def __init__(self, text: str, on_click: Optional[Callable] = None):
        super().__init__()
        self.tag_name = "button"
        self.set_prop('text', text)
        if on_click:
            self.set_prop('on_click', on_click)
        
    def render(self) -> Element:
        button = Element(self.tag_name, text=self.props['text'])
        if 'on_click' in self.props:
            button.on('click', self.props['on_click'])
        return button

class Container(Component):
    """预构建的Container组件"""
    
    def __init__(self, *children: Component):
        super().__init__()
        for child in children:
            self.add_child(child)
        
    def render(self) -> Element:
        container = Element(self.tag_name)
        for child in self.children:
            container.add(child.render())
        return container

class Input(Component):
    """预构建的Input组件"""
    
    def __init__(self, placeholder: str = "", value: str = "", on_change: Optional[Callable] = None):
        super().__init__()
        self.tag_name = "input"
        self.set_prop('placeholder', placeholder)
        self.set_prop('value', value)
        if on_change:
            self.set_prop('on_change', on_change)
        
    def render(self) -> Element:
        input_elem = Element(self.tag_name)
        input_elem.set_attr('placeholder', self.props['placeholder'])
        input_elem.set_attr('value', self.props['value'])
        if 'on_change' in self.props:
            input_elem.on('change', self.props['on_change'])
        return input_elem

class Form(Component):
    """预构建的Form组件"""
    
    def __init__(self, on_submit: Optional[Callable] = None):
        super().__init__()
        self.tag_name = "form"
        if on_submit:
            self.set_prop('on_submit', on_submit)
        
    def render(self) -> Element:
        form = Element(self.tag_name)
        if 'on_submit' in self.props:
            form.on('submit', self.props['on_submit'])
        for child in self.children:
            form.add(child.render())
        return form

class Text(Component):
    """文本组件"""
    
    def __init__(self, text: str, tag: str = "span"):
        super().__init__()
        self.tag_name = tag
        self.set_prop('text', text)
        
    def render(self) -> Element:
        return Element(self.tag_name, text=self.text)

class Image(Component):
    """图像组件"""
    
    def __init__(self, src: str, alt: str = "", width: str = "", height: str = ""):
        super().__init__()
        self.tag_name = "img"
        self.set_prop('src', src)
        self.set_prop('alt', alt)
        if width:
            self.set_prop('width', width)
        if height:
            self.set_prop('height', height)
        
    def render(self) -> Element:
        img = Element(self.tag_name)
        img.set_attr('src', self.src)
        img.set_attr('alt', self.alt)
        if 'width' in self.props:
            img.set_attr('width', self.width)
        if 'height' in self.props:
            img.set_attr('height', self.height)
        return img

class Link(Component):
    """链接组件"""
    
    def __init__(self, href: str, text: str = "", target: str = "_self"):
        super().__init__()
        self.tag_name = "a"
        self.set_prop('href', href)
        self.set_prop('text', text)
        self.set_prop('target', target)
        
    def render(self) -> Element:
        link = Element(self.tag_name, text=self.text)
        link.set_attr('href', self.href)
        link.set_attr('target', self.target)
        return link

class List(Component):
    """列表组件"""
    
    def __init__(self, items: list[str] | None = None, ordered: bool = False):
        super().__init__()
        self.tag_name = "ol" if ordered else "ul"
        self.set_prop('items', items or [])

    def add_item(self, item: str):
        if 'items' not in self.props:
            self.props['items'] = []
        self.props['items'].append(item)
        
    def render(self) -> Element:
        list_elem = Element(self.tag_name)
        for item in self.props.get('items', []):
            li = Element('li', text=str(item))
            list_elem.add(li)
        return list_elem

class Card(Component):
    """卡片组件"""
    
    def __init__(self, title: str = "", body: str = "", footer: str = ""):
        super().__init__()
        self.tag_name = "div"
        self.set_prop('title', title)
        self.set_prop('body', body)
        self.set_prop('footer', footer)
        
    def render(self) -> Element:
        card = Element(self.tag_name)
        card.add_class('card')
        
        if self.title:
            header = Element('div')
            header.add_class('card-header')
            header.add(Element('h3', text=self.title))
            card.add(header)
            
        body = Element('div')
        body.add_class('card-body')
        body.add(Element('p', text=self.body))
        card.add(body)
        
        if self.footer:
            footer = Element('div')
            footer.add_class('card-footer')
            footer.add(Element('p', text=self.footer))
            card.add(footer)
            
        return card

class Grid(Component):
    """网格布局组件"""
    
    def __init__(self, columns: int = 12, gap: str = "1rem"):
        super().__init__()
        self.tag_name = "div"
        self.set_prop('columns', columns)
        self.set_prop('gap', gap)
        self.style.add(
            display="grid",
            grid_template_columns=f"repeat({columns}, 1fr)",
            gap=gap
        )
        
    def add_item(self, component: Component, column_span: int = 1):
        component.style.add(grid_column=f"span {column_span}")
        self.add_child(component)
        
    def render(self) -> Element:
        grid = Element(self.tag_name)
        for child in self.children:
            grid.add(child.render())
        return grid

class Select(Component):
    """选择组件"""
    
    def __init__(self, options: OptionsType, value: str = "", on_change: Optional[Callable] = None):
        super().__init__()
        self.tag_name = "select"
        self.set_prop('options', options)
        self.set_prop('value', value)
        if on_change:
            self.set_prop('on_change', on_change)
        
    def render(self) -> Element:
        select = Element(self.tag_name)
        if 'on_change' in self.props:
            select.on('change', self.on_change)
            
        for option in self.options:
            opt = Element('option')
            opt.set_attr('value', option.get('value', ''))
            if option.get('value') == self.value:
                opt.set_attr('selected', 'selected')
            opt.text = option.get('label', option.get('value', ''))
            select.add(opt)
            
        return select

class Checkbox(Component):
    """复选框组件"""
    
    def __init__(self, label: str = "", checked: bool = False, on_change: Optional[Callable] = None):
        super().__init__()
        self.tag_name = "input"
        self.set_prop('type', 'checkbox')
        self.set_prop('label', label)
        self.set_prop('checked', checked)
        if on_change:
            self.set_prop('on_change', on_change)
        
    def render(self) -> Element:
        container = Element('div')
        
        input_elem = Element(self.tag_name)
        input_elem.set_attr('type', 'checkbox')
        if self.checked:
            input_elem.set_attr('checked', 'checked')
        if 'on_change' in self.props:
            input_elem.on('change', self.on_change)
        container.add(input_elem)
        
        if self.label:
            label = Element('label')
            label.text = self.label
            container.add(label)
            
        return container

class Radio(Component):
    """单选框组件"""
    
    def __init__(self, name: str, value: str, label: str = "", checked: bool = False, on_change: Optional[Callable] = None):
        super().__init__()
        self.tag_name = "input"
        self.set_prop('type', 'radio')
        self.set_prop('name', name)
        self.set_prop('value', value)
        self.set_prop('label', label)
        self.set_prop('checked', checked)
        if on_change:
            self.set_prop('on_change', on_change)
        
    def render(self) -> Element:
        container = Element('div')
        
        input_elem = Element(self.tag_name)
        input_elem.set_attr('type', 'radio')
        input_elem.set_attr('name', self.name)
        input_elem.set_attr('value', self.value)
        if self.checked:
            input_elem.set_attr('checked', 'checked')
        if 'on_change' in self.props:
            input_elem.on('change', self.on_change)
        container.add(input_elem)
        
        if self.label:
            label = Element('label')
            label.text = self.label
            container.add(label)
            
        return container

class TextArea(Component):
    """文本域组件"""
    
    def __init__(self, value: str = "", placeholder: str = "", rows: int = 3, on_change: Optional[Callable] = None):
        super().__init__()
        self.tag_name = "textarea"
        self.set_prop('value', value)
        self.set_prop('placeholder', placeholder)
        self.set_prop('rows', rows)
        if on_change:
            self.set_prop('on_change', on_change)
        
    def render(self) -> Element:
        textarea = Element(self.tag_name, text=self.value)
        textarea.set_attr('placeholder', self.placeholder)
        textarea.set_attr('rows', str(self.rows))
        if 'on_change' in self.props:
            textarea.on('change', self.on_change)
        return textarea

class Navbar(Component):
    """导航栏组件"""
    
    def __init__(self, brand: str = "", items: list[dict[str, str]] = None, theme: str = "light"):
        super().__init__()
        self.tag_name = "nav"
        self.set_prop('brand', brand)
        self.set_prop('items', items or [])
        self.set_prop('theme', theme)
        self.style.add(
            display="flex",
            align_items="center",
            padding="1rem",
            background_color="#ffffff" if theme == "light" else "#343a40",
            color="#000000" if theme == "light" else "#ffffff"
        )
        
    def add_item(self, text: str, href: str = "#", active: bool = False):
        self.props['items'].append({
            'text': text,
            'href': href,
            'active': active
        })
        
    def render(self) -> Element:
        nav = Element(self.tag_name)
        
        if self.brand:
            brand = Element('a')
            brand.add_class('navbar-brand')
            brand.set_attr('href', '#')
            brand.text = self.brand
            brand.style.add(
                font_size="1.25rem",
                padding_right="1rem",
                text_decoration="none",
                color="inherit"
            )
            nav.add(brand)
            
        items_container = Element('div')
        items_container.add_class('navbar-items')
        items_container.style.add(
            display="flex",
            gap="1rem"
        )
        
        for item in self.items:
            link = Element('a')
            link.set_attr('href', item.get('href', '#'))
            link.text = item.get('text', '')
            link.style.add(
                text_decoration="none",
                color="inherit"
            )
            if item.get('active'):
                link.style.add(font_weight="bold")
            items_container.add(link)
            
        nav.add(items_container)
        return nav

class Flex(Component):
    """Flexbox容器组件"""
    
    def __init__(self, direction: str = "row", justify: str = "flex-start", align: str = "stretch", wrap: bool = False, gap: str = "0"):
        super().__init__()
        self.tag_name = "div"
        self.style.add(
            display="flex",
            flex_direction=direction,
            justify_content=justify,
            align_items=align,
            flex_wrap="wrap" if wrap else "nowrap",
            gap=gap
        )
        
    def render(self) -> Element:
        flex = Element(self.tag_name)
        for child in self.children:
            flex.add(child.render())
        return flex

class Modal(Component):
    """模态对话框组件"""
    
    def __init__(self, content: str, title: str = "", show_close: bool = True):
        super().__init__()
        self.tag_name = "div"
        self.set_prop('content', content)
        self.set_prop('title', title)
        self.set_prop('show_close', show_close)
        
    def render(self) -> Element:
        close_button = '<span class="modal-close">&times;</span>' if self.show_close else ''
        title_html = f'<div class="modal-title">{self.title}</div>' if self.title else ''
        
        return f"""
        <div class="pytoweb-modal">
            <div class="modal-content">
                <div class="modal-header">
                    {title_html}
                    {close_button}
                </div>
                <div class="modal-body">
                    {self.content}
                </div>
            </div>
        </div>
        """

class Toast(Component):
    """吐司通知组件"""
    
    def __init__(self, message: str, type: str = "info", duration: int = 3000):
        super().__init__()
        self.tag_name = "div"
        self.set_prop('message', message)
        self.set_prop('type', type)
        self.set_prop('duration', duration)
        
    def render(self) -> Element:
        return f"""
        <div class="pytoweb-toast {self.type}" style="display: none;">
            {self.message}
        </div>
        <script>
            (function() {{
                const toast = document.querySelector('.pytoweb-toast');
                toast.style.display = 'block';
                setTimeout(() => {{
                    toast.style.display = 'none';
                }}, {self.duration});
            }})();
        </script>
        """

class Tabs(Component):
    """选项卡组件"""
    
    def __init__(self, tabs: list[dict[str, str]]):
        """
        初始化选项卡组件
        tabs: 选项卡列表，每个选项卡是一个字典，包含'label'和'content'键
        """
        super().__init__()
        self.tag_name = "div"
        self.set_prop('tabs', tabs)
        
    def render(self) -> Element:
        tabs_html = "".join([
            f'<div class="tab-button" data-tab="{i}">{tab["label"]}</div>'
            for i, tab in enumerate(self.tabs)
        ])
        
        content_html = "".join([
            f'<div class="tab-content" data-tab="{i}">{tab["content"]}</div>'
            for i, tab in enumerate(self.tabs)
        ])
        
        return f"""
        <div class="pytoweb-tabs">
            <div class="tab-buttons">
                {tabs_html}
            </div>
            <div class="tab-contents">
                {content_html}
            </div>
        </div>
        <script>
            (function() {{
                const tabButtons = document.querySelectorAll('.tab-button');
                const tabContents = document.querySelectorAll('.tab-content');
                
                tabButtons.forEach(button => {{
                    button.addEventListener('click', () => {{
                        const tabIndex = button.dataset.tab;
                        
                        tabButtons.forEach(btn => btn.classList.remove('active'));
                        tabContents.forEach(content => content.classList.remove('active'));
                        
                        button.classList.add('active');
                        document.querySelector(`.tab-content[data-tab="${{tabIndex}}"]`).classList.add('active');
                    }});
                }});
                
                // Activate first tab by default
                tabButtons[0]?.click();
            }})();
        </script>
        """

class DatePicker(Component):
    """日期选择器组件"""
    
    def __init__(self, value: str = "", format: str = "YYYY-MM-DD", 
                 min_date: str = None, max_date: str = None,
                 on_change: Optional[Callable] = None):
        super().__init__()
        self.tag_name = "div"
        self.set_prop('value', value)
        self.set_prop('format', format)
        self.set_prop('min_date', min_date)
        self.set_prop('max_date', max_date)
        if on_change:
            self.set_prop('on_change', on_change)
            
        # Add calendar container
        self.calendar = Element('div')
        self.calendar.style.add(
            position="absolute",
            display="none",
            background_color="#ffffff",
            border="1px solid #ddd",
            border_radius="4px",
            padding="1rem",
            box_shadow="0 2px 10px rgba(0,0,0,0.1)",
            z_index="1000"
        )
        
    def render(self):
        input_field = Element('input')
        input_field.set_prop('type', 'text')
        input_field.set_prop('value', self.props.get('value', ''))
        input_field.set_prop('placeholder', self.props.get('format'))
        input_field.style.add(
            padding="0.5rem",
            border="1px solid #ddd",
            border_radius="4px",
            font_size="1rem"
        )
        
        container = Element('div')
        container.style.add(position="relative")
        container.add(input_field)
        container.add(self.calendar)
        
        return container

class Table(Component):
    """表格组件"""
    
    def __init__(self, columns: list[dict[str, str]], data: list[dict[str, Any]],
                 sortable: bool = True, filterable: bool = True,
                 page_size: int = 10):
        super().__init__()
        self.tag_name = "div"
        self.set_prop('columns', columns)  # [{"key": "id", "title": "ID"}, ...]
        self.set_prop('data', data)
        self.set_prop('sortable', sortable)
        self.set_prop('filterable', filterable)
        self.set_prop('page_size', page_size)
        self.set_prop('current_page', 1)
        
        # State for sorting and filtering
        self.state['sort_key'] = None
        self.state['sort_order'] = 'asc'
        self.state['filters'] = {}
        
    def render(self):
        container = Element('div')
        
        # Create table element
        table = Element('table')
        table.style.add(
            width="100%",
            border_collapse="collapse",
            margin="1rem 0"
        )
        
        # Render header
        header = Element('thead')
        header_row = Element('tr')
        
        for col in self.props['columns']:
            th = Element('th')
            th.style.add(
                padding="0.75rem",
                border_bottom="2px solid #ddd",
                text_align="left",
                font_weight="bold"
            )
            
            if self.props['sortable']:
                sort_container = Element('div')
                sort_container.style.add(
                    display="flex",
                    align_items="center",
                    cursor="pointer"
                )
                sort_container.add(Element('span', text=col['title']))
                sort_container.add(Element('span', text="↕️", style={"margin-left": "0.5rem"}))
                th.add(sort_container)
            else:
                th.add(Element('span', text=col['title']))
                
            header_row.add(th)
            
        header.add(header_row)
        table.add(header)
        
        # Render body
        body = Element('tbody')
        
        # Apply pagination
        start_idx = (self.props['current_page'] - 1) * self.props['page_size']
        end_idx = start_idx + self.props['page_size']
        page_data = self.props['data'][start_idx:end_idx]
        
        for row_data in page_data:
            tr = Element('tr')
            tr.style.add(
                border_bottom="1px solid #ddd",
                transition="background-color 0.2s"
            )
            tr.add_hover_style(background_color="#f5f5f5")
            
            for col in self.props['columns']:
                td = Element('td')
                td.style.add(padding="0.75rem")
                td.add(Element('span', text=str(row_data.get(col['key'], ''))))
                tr.add(td)
                
            body.add(tr)
            
        table.add(body)
        container.add(table)
        
        # Add pagination
        if len(self.props['data']) > self.props['page_size']:
            pagination = self._render_pagination()
            container.add(pagination)
        
        return container
        
    def _render_pagination(self):
        total_pages = (len(self.props['data']) + self.props['page_size'] - 1) // self.props['page_size']
        
        pagination = Element('div')
        pagination.style.add(
            display="flex",
            justify_content="center",
            align_items="center",
            margin_top="1rem"
        )
        
        # Previous button
        prev_btn = Element('button')
        prev_btn.add(Element('span', text="Previous"))
        prev_btn.style.add(
            padding="0.5rem 1rem",
            margin="0 0.25rem",
            border="1px solid #ddd",
            border_radius="4px",
            cursor="pointer" if self.props['current_page'] > 1 else "not-allowed",
            background_color="#fff"
        )
        pagination.add(prev_btn)
        
        # Page numbers
        for page in range(1, total_pages + 1):
            page_btn = Element('button')
            page_btn.add(Element('span', text=str(page)))
            page_btn.style.add(
                padding="0.5rem 1rem",
                margin="0 0.25rem",
                border="1px solid #ddd",
                border_radius="4px",
                cursor="pointer",
                background_color="#fff" if page != self.props['current_page'] else "#e6e6e6"
            )
            pagination.add(page_btn)
            
        # Next button
        next_btn = Element('button')
        next_btn.add(Element('span', text="Next"))
        next_btn.style.add(
            padding="0.5rem 1rem",
            margin="0 0.25rem",
            border="1px solid #ddd",
            border_radius="4px",
            cursor="pointer" if self.props['current_page'] < total_pages else "not-allowed",
            background_color="#fff"
        )
        pagination.add(next_btn)
        
        return pagination

class Tree(Component):
    """树形组件"""
    
    def __init__(self, data: list[dict[str, Any]], expanded: bool = False):
        """
        初始化树形组件
        data: 树形数据，每个节点是一个字典，包含'id'、'label'、'children'等键
        """
        super().__init__()
        self.tag_name = "div"
        self.set_prop('data', data)
        self.state['expanded'] = set()  # Store expanded node IDs
        
        # Expand all nodes if expanded is True
        if expanded:
            self._expand_all(data)
            
    def _expand_all(self, nodes: list[dict[str, Any]]):
        """递归展开所有节点"""
        for node in nodes:
            self.state['expanded'].add(node['id'])
            if 'children' in node and node['children']:
                self._expand_all(node['children'])

    def toggle_node(self, node_id: str):
        """Toggle node expansion state"""
        if node_id in self.state['expanded']:
            self.state['expanded'].remove(node_id)
        else:
            self.state['expanded'].add(node_id)
        self._update()
        
    def _render_node(self, node: dict[str, Any], level: int = 0) -> Element:
        """Render a single node and its children"""
        node_container = Element('div')
        
        # Node header
        header = Element('div')
        header.style.add(
            display="flex",
            align_items="center",
            padding="0.5rem",
            padding_left=f"{level * 1.5 + 0.5}rem",
            cursor="pointer",
            transition="background-color 0.2s"
        )
        header.add_hover_style(background_color="#f5f5f5")
        
        # Expand/collapse icon
        has_children = 'children' in node and node['children']
        if has_children:
            icon = Element('span')
            icon.style.add(
                margin_right="0.5rem",
                transition="transform 0.2s"
            )
            if node['id'] in self.state['expanded']:
                icon.style.add(transform="rotate(90deg)")
            icon.add(Element('span', text="▶"))
            header.add(icon)
            
        # Node icon (if provided)
        if 'icon' in node:
            node_icon = Element('span')
            node_icon.style.add(margin_right="0.5rem")
            node_icon.add(Element('span', text=node['icon']))
            header.add(node_icon)
            
        # Node label
        label = Element('span')
        label.add(Element('span', text=node['label']))
        header.add(label)
        
        # Add click handler for expansion toggle
        if has_children:
            header.on('click', lambda: self.toggle_node(node['id']))
            
        node_container.add(header)
        
        # Render children if node is expanded
        if has_children and node['id'] in self.state['expanded']:
            children_container = Element('div')
            for child in node['children']:
                children_container.add(self._render_node(child, level + 1))
            node_container.add(children_container)
            
        return node_container
        
    def render(self):
        container = Element('div')
        container.style.add(
            border="1px solid #ddd",
            border_radius="4px",
            overflow="hidden"
        )
        
        # Render each root node
        for node in self.props['data']:
            container.add(self._render_node(node))
            
        return container

class Responsive(Component):
    """响应式容器组件"""
    breakpoints = {
        'sm': '576px',
        'md': '768px',
        'lg': '992px',
        'xl': '1200px',
        'xxl': '1400px'
    }
    
    def __init__(self):
        super().__init__()
        self.tag_name = "div"
        self.style.add(
            width="100%",
            margin="0 auto",
            padding="0 15px",
            box_sizing="border-box"
        )
        
    def add_media_query(self, breakpoint: str, styles: dict[str, str]):
        self.style.add_media_query(
            f"(min-width: {self.breakpoints[breakpoint]})",
            styles
        )
        return self

class Skeleton(Component):
    """骨架屏组件"""
    def __init__(self, type: str = "text", rows: int = 1, height: str = "1rem"):
        super().__init__()
        self.tag_name = "div"
        self.set_prop('type', type)
        self.set_prop('rows', rows)
        self.set_prop('height', height)
        self.style.add(
            background="linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)",
            background_size="200% 100%",
            animation="skeleton-loading 1.5s infinite",
            border_radius="4px",
            height=height,
            margin_bottom="0.5rem"
        )

class Carousel(Component):
    """幻灯片组件"""
    def __init__(self, images: list[dict[str, str]], auto_play: bool = True, interval: int = 3000):
        super().__init__()
        self.tag_name = "div"
        self.set_prop('images', images)  # [{"src": "...", "alt": "..."}]
        self.set_prop('auto_play', auto_play)
        self.set_prop('interval', interval)
        self.state['current_index'] = 0
        self.style.add(
            position="relative",
            overflow="hidden",
            width="100%",
            height="100%"
        )

class Drawer(Component):
    """抽屉组件"""
    def __init__(self, content: Component, position: str = "left", width: str = "300px"):
        super().__init__()
        self.tag_name = "div"
        self.set_prop('content', content)
        self.set_prop('position', position)
        self.set_prop('width', width)
        self.state['visible'] = False
        self.style.add(
            position="fixed",
            top="0",
            height="100%",
            background_color="#ffffff",
            box_shadow="0 0 10px rgba(0,0,0,0.1)",
            transition="transform 0.3s ease-in-out",
            z_index="1000"
        )

class Progress(Component):
    """进度条组件"""
    def __init__(self, value: int = 0, max: int = 100, type: str = "bar", color: str = "#007bff"):
        super().__init__()
        self.tag_name = "div"
        self.set_prop('value', value)
        self.set_prop('max', max)
        self.set_prop('type', type)
        self.set_prop('color', color)
        self.style.add(
            width="100%",
            height="0.5rem",
            background_color="#e9ecef",
            border_radius="0.25rem",
            overflow="hidden"
        )

class Tooltip(Component):
    """提示框组件"""
    def __init__(self, content: str, position: str = "top"):
        super().__init__()
        self.tag_name = "div"
        self.set_prop('content', content)
        self.set_prop('position', position)
        self.style.add(
            position="relative",
            display="inline-block"
        )

class Badge(Component):
    """徽章组件"""
    def __init__(self, text: str, type: str = "primary", pill: bool = False):
        super().__init__()
        self.tag_name = "span"
        self.set_prop('text', text)
        self.set_prop('type', type)
        self.set_prop('pill', pill)
        self.style.add(
            display="inline-block",
            padding="0.25em 0.4em",
            font_size="75%",
            font_weight="700",
            line_height="1",
            text_align="center",
            white_space="nowrap",
            vertical_align="baseline",
            border_radius="0.25rem" if not pill else "10rem",
            color="#fff",
            background_color=self._get_type_color(type)
        )

    def _get_type_color(self, type: str) -> str:
        colors = {
            'primary': '#007bff',
            'secondary': '#6c757d',
            'success': '#28a745',
            'danger': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8'
        }
        return colors.get(type, colors['primary'])

class ModernModal(Component):
    """现代模态对话框组件"""
    def __init__(self,
                 title: str,
                 content: str,
                 size: str = "md",
                 centered: bool = True,
                 closable: bool = True):
        super().__init__()
        self.tag_name = "div"
        self.set_prop('title', title)
        self.set_prop('content', content)
        self.set_prop('size', size)
        self.set_prop('centered', centered)
        self.set_prop('closable', closable)
        
        self.state.update({
            'visible': False
        })
        
        # 设置样式
        self.style.add(
            position="fixed",
            top="0",
            left="0",
            width="100%",
            height="100%",
            display="flex",
            align_items="center" if centered else "flex-start",
            justify_content="center",
            background_color="rgba(0, 0, 0, 0.5)",
            z_index="1000",
            opacity="0",
            visibility="hidden",
            transition="opacity 0.3s ease-in-out, visibility 0.3s ease-in-out"
        )
        
    def show(self):
        """显示模态对话框"""
        self.set_state('visible', True)
        self.style.add(
            opacity="1",
            visibility="visible"
        )
        
    def hide(self):
        """隐藏模态对话框"""
        self.set_state('visible', False)
        self.style.add(
            opacity="0",
            visibility="hidden"
        )
        
    def render(self):
        """渲染模态对话框"""
        dialog = Component()
        dialog.tag_name = "div"
        dialog.style.add(
            background_color="#ffffff",
            border_radius="0.5rem",
            box_shadow="0 25px 50px -12px rgba(0, 0, 0, 0.25)",
            max_width=self._get_size_width(),
            width="100%",
            max_height="90vh",
            display="flex",
            flex_direction="column",
            transform=f"scale({1 if self.state['visible'] else 0.9})",
            transition="transform 0.3s ease-in-out"
        )
        
        # Header
        header = Component()
        header.tag_name = "div"
        header.style.add(
            padding="1rem",
            border_bottom="1px solid #e5e7eb",
            display="flex",
            align_items="center",
            justify_content="space-between"
        )
        
        title = Component()
        title.tag_name = "h3"
        title.style.add(
            margin="0",
            font_size="1.25rem",
            font_weight="600",
            color="#111827"
        )
        title.set_text(self.props['title'])
        header.add_child(title)
        
        if self.props['closable']:
            close_button = Component()
            close_button.tag_name = "button"
            close_button.style.add(
                background="none",
                border="none",
                padding="0.5rem",
                cursor="pointer",
                color="#6b7280"
            )
            close_button.set_text("×")
            close_button.on_click.add(self.hide)
            header.add_child(close_button)
            
        dialog.add_child(header)
        
        # Content
        content = Component()
        content.tag_name = "div"
        content.style.add(
            padding="1rem",
            overflow_y="auto"
        )
        
        if isinstance(self.props['content'], str):
            content.set_text(self.props['content'])
        else:
            content.add_child(self.props['content'])
            
        dialog.add_child(content)
        
        return dialog
        
    def _get_size_width(self) -> str:
        """Get modal width based on size"""
        sizes = {
            "sm": "28rem",
            "md": "32rem",
            "lg": "48rem",
            "xl": "64rem",
            "full": "100%"
        }
        return sizes.get(self.props['size'], sizes['md'])

class ModernTabs(Component):
    """现代选项卡组件"""
    
    def __init__(self,
                 tabs: list[dict[str, Any]],
                 active_index: int = 0,
                 variant: str = "default"):
        super().__init__()
        self.tag_name = "div"
        self.set_prop('tabs', tabs)
        self.set_prop('variant', variant)
        
        self.state.update({
            'active_index': active_index
        })

    def _handle_tab_click(self, index: int):
        """Handle tab click"""
        self.set_state('active_index', index)
        
    def render(self):
        """Render tabs"""
        container = Component()
        container.tag_name = "div"
        
        # Tab list
        tab_list = Component()
        tab_list.tag_name = "div"
        tab_list.style.add(
            display="flex",
            border_bottom="1px solid #e5e7eb"
        )
        
        for i, tab in enumerate(self.props['tabs']):
            tab_button = Component()
            tab_button.tag_name = "button"
            tab_button.style.add(
                padding="0.75rem 1rem",
                border="none",
                background="none",
                font_weight="500",
                color="#6b7280" if i != self.state['active_index'] else "#111827",
                border_bottom=f"2px solid {'transparent' if i != self.state['active_index'] else '#3b82f6'}",
                cursor="pointer",
                transition="all 0.2s ease-in-out"
            )
            tab_button.set_text(tab['label'])
            tab_button.on_click.add(lambda e, i=i: self._handle_tab_click(i))
            tab_list.add_child(tab_button)
            
        container.add_child(tab_list)
        
        # Tab panels
        panel_container = Component()
        panel_container.tag_name = "div"
        panel_container.style.add(
            padding="1rem"
        )
        
        active_tab = self.props['tabs'][self.state['active_index']]
        if isinstance(active_tab['content'], str):
            panel_container.set_text(active_tab['content'])
        else:
            panel_container.add_child(active_tab['content'])
            
        container.add_child(panel_container)
        
        return container

class ModernAccordion(Component):
    """现代手风琴组件"""
    
    def __init__(self,
                 items: list[dict[str, Any]],
                 multiple: bool = False):
        super().__init__()
        self.tag_name = "div"
        self.set_prop('items', items)
        self.set_prop('multiple', multiple)
        
        self.state.update({
            'expanded': set()
        })

    def _toggle_item(self, index: int):
        """Toggle accordion item"""
        expanded = self.state['expanded'].copy()
        
        if not self.props['multiple']:
            expanded.clear()
            
        if index in expanded:
            expanded.remove(index)
        else:
            expanded.add(index)
            
        self.set_state('expanded', expanded)
        
    def render(self):
        """Render accordion"""
        container = Component()
        container.tag_name = "div"
        container.style.add(
            border="1px solid #e5e7eb",
            border_radius="0.5rem",
            overflow="hidden"
        )
        
        for i, item in enumerate(self.props['items']):
            # Item container
            item_container = Component()
            item_container.tag_name = "div"
            item_container.style.add(
                border_top="1px solid #e5e7eb" if i > 0 else "none"
            )
            
            # Header
            header = Component()
            header.tag_name = "button"
            header.style.add(
                width="100%",
                padding="1rem",
                background="none",
                border="none",
                text_align="left",
                cursor="pointer",
                display="flex",
                align_items="center",
                justify_content="space-between"
            )
            
            # Title
            title = Component()
            title.tag_name = "span"
            title.style.add(
                font_weight="500",
                color="#111827"
            )
            title.set_text(item['title'])
            header.add_child(title)
            
            # Icon
            icon = Component()
            icon.tag_name = "span"
            icon.style.add(
                transform=f"rotate({90 if i in self.state['expanded'] else 0}deg)",
                transition="transform 0.2s ease-in-out"
            )
            icon.set_text("›")
            header.add_child(icon)
            
            header.on_click.add(lambda e, i=i: self._toggle_item(i))
            item_container.add_child(header)
            
            # Content
            content = Component()
            content.tag_name = "div"
            content.style.add(
                padding="0 1rem",
                max_height=f"{'none' if i in self.state['expanded'] else '0'}",
                overflow="hidden",
                transition="max-height 0.3s ease-in-out"
            )
            
            if isinstance(item['content'], str):
                content.set_text(item['content'])
            else:
                content.add_child(item['content'])
                
            item_container.add_child(content)
            container.add_child(item_container)
            
        return container

class ModernToast(Component):
    """现代吐司通知组件"""
    
    def __init__(self,
                 message: str,
                 type: str = "info",
                 duration: int = 3000,
                 position: str = "bottom-right"):
        super().__init__()
        self.tag_name = "div"
        self.set_prop('message', message)
        self.set_prop('type', type)
        self.set_prop('duration', duration)
        self.set_prop('position', position)
        
        self.state.update({
            'visible': False
        })
        
        # 设置样式
        self.style.add(
            position="fixed",
            padding="1rem",
            border_radius="0.5rem",
            background_color=self._get_background_color(),
            color="#ffffff",
            box_shadow="0 10px 15px -3px rgba(0, 0, 0, 0.1)",
            max_width="24rem",
            opacity="0",
            transform="translateY(1rem)",
            transition="opacity 0.3s ease-in-out, transform 0.3s ease-in-out",
            **self._get_position_style()
        )
        
    def show(self):
        """显示吐司通知"""
        self.set_state('visible', True)
        self.style.add(
            opacity="1",
            transform="translateY(0)"
        )
        
        # Auto hide
        if self.props['duration'] > 0:
            def hide():
                self.hide()
            setTimeout(hide, self.props['duration'])
            
    def hide(self):
        """隐藏吐司通知"""
        self.set_state('visible', False)
        self.style.add(
            opacity="0",
            transform="translateY(1rem)"
        )
        
    def _get_background_color(self) -> str:
        """Get background color based on type"""
        colors = {
            "info": "#3b82f6",
            "success": "#10b981",
            "warning": "#f59e0b",
            "error": "#ef4444"
        }
        return colors.get(self.props['type'], colors['info'])
        
    def _get_position_style(self) -> dict[str, str]:
        """Get position style"""
        positions = {
            "top-left": {"top": "1rem", "left": "1rem"},
            "top-right": {"top": "1rem", "right": "1rem"},
            "bottom-left": {"bottom": "1rem", "left": "1rem"},
            "bottom-right": {"bottom": "1rem", "right": "1rem"}
        }
        return positions.get(self.props['position'], positions['bottom-right'])
        
    def render(self):
        """Render toast"""
        container = Component()
        container.tag_name = "div"
        container.style.add(
            display="flex",
            align_items="center",
            gap="0.5rem"
        )
        
        # Icon
        icon = Component()
        icon.tag_name = "span"
        icon.style.add(
            font_size="1.25rem"
        )
        icon.set_text(self._get_icon())
        container.add_child(icon)
        
        # Message
        message = Component()
        message.tag_name = "span"
        message.set_text(self.props['message'])
        container.add_child(message)
        
        return container
        
    def _get_icon(self) -> str:
        """Get icon based on type"""
        icons = {
            "info": "ℹ",
            "success": "✓",
            "warning": "⚠",
            "error": "✕"
        }
        return icons.get(self.props['type'], icons['info'])

class VirtualList(Component):
    """虚拟滚动列表组件"""
    
    def __init__(self, 
                 items: list[Any],
                 item_height: int = 40,
                 viewport_height: int = 400,
                 overscan: int = 3,
                 render_item: Callable[[Any], Component] | None = None):
        super().__init__()
        self.tag_name = "div"
        self.set_prop('items', items)
        self.set_prop('item_height', item_height)
        self.set_prop('viewport_height', viewport_height)
        self.set_prop('overscan', overscan)
        self.set_prop('render_item', render_item or self._default_render_item)
        
        self.state.update({
            'scroll_top': 0,
            'start_index': 0,
            'end_index': 0,
            'rendered_items': {}  # 缓存已渲染的项
        })
        
        # 设置容器样式
        self.style.add(
            position="relative",
            height=f"{viewport_height}px",
            overflow_y="auto"
        )
        
        # 监听滚动事件
        self.on_scroll = EventDelegate()
        self.on_scroll.add(self._handle_scroll)
        
    def _handle_scroll(self, event: dict[str, Any]):
        """处理滚动事件"""
        try:
            scroll_top = event.get('target', {}).get('scrollTop', 0)
            self._update_visible_range(scroll_top)
        except Exception as e:
            self._logger.error(f"Error handling scroll: {e}", exc_info=True)
        
    def _update_visible_range(self, scroll_top: int):
        """更新可见项范围"""
        try:
            item_height = self.props['item_height']
            viewport_height = self.props['viewport_height']
            overscan = self.props['overscan']
            total_items = len(self.props['items'])
            
            # 计算可见范围
            start = max(0, scroll_top // item_height - overscan)
            end = min(
                total_items,
                (scroll_top + viewport_height) // item_height + overscan
            )
            
            if start != self.state['start_index'] or end != self.state['end_index']:
                self.state.update({
                    'scroll_top': scroll_top,
                    'start_index': start,
                    'end_index': end
                })
                self._update()
                
        except Exception as e:
            self._logger.error(f"Error updating visible range: {e}", exc_info=True)
        
    def _default_render_item(self, item: Any) -> Component:
        """默认项渲染器"""
        text = Text(str(item))
        text.style.add(padding="0.5rem")
        return text
        
    def render(self) -> Element:
        """渲染虚拟列表"""
        try:
            container = super().render()
            items = self.props['items']
            item_height = self.props['item_height']
            start = self.state['start_index']
            end = self.state['end_index']
            
            # 创建内容容器
            content = Element('div')
            content.style.add(
                height=f"{len(items) * item_height}px",
                position="relative"
            )
            
            # 只渲染可见范围内的项
            for i in range(start, end):
                if i >= len(items):
                    break
                    
                item = items[i]
                item_key = f"item_{i}"
                
                # 检查缓存
                if item_key not in self.state['rendered_items']:
                    self.state['rendered_items'][item_key] = self.props['render_item'](item)
                    
                item_component = self.state['rendered_items'][item_key]
                item_element = item_component.render()
                item_element.style.add(
                    position="absolute",
                    top=f"{i * item_height}px",
                    left="0",
                    right="0",
                    height=f"{item_height}px"
                )
                
                content.append_child(item_element)
                
            # 清理不可见项的缓存
            visible_keys = {f"item_{i}" for i in range(start, end)}
            self.state['rendered_items'] = {
                k: v for k, v in self.state['rendered_items'].items()
                if k in visible_keys
            }
            
            container.append_child(content)
            return container
            
        except Exception as e:
            self._logger.error(f"Error rendering virtual list: {e}", exc_info=True)
            raise

class DraggableList(Component):
    """可拖放的列表组件"""
    
    def __init__(self, 
                 items: list[Any],
                 render_item: Callable[[Any], Component] | None = None,
                 on_reorder: Optional[Callable[[list[Any]], None]] = None):
        super().__init__()
        self.tag_name = "div"
        self.set_prop('items', items)
        self.set_prop('render_item', render_item or self._default_render_item)
        self.set_prop('on_reorder', on_reorder)
        
        self.state.update({
            'dragging_index': None,
            'drag_over_index': None,
            'items': items.copy()
        })
        
        # 设置容器样式
        self.style.add(
            position="relative",
            user_select="none"
        )
        
    def _default_render_item(self, item: Any) -> Component:
        """默认项渲染器"""
        text = Text(str(item))
        text.style.add(
            padding="1rem",
            background_color="#ffffff",
            border="1px solid #e0e0e0",
            margin_bottom="0.5rem",
            cursor="move"
        )
        return text
        
    def _handle_drag_start(self, index: int, event: dict[str, Any]):
        """处理拖拽开始事件"""
        try:
            self.state['dragging_index'] = index
            self._update()
        except Exception as e:
            self._logger.error(f"Error handling drag start: {e}", exc_info=True)
        
    def _handle_drag_over(self, index: int, event: dict[str, Any]):
        """处理拖拽悬停事件"""
        try:
            if index != self.state['drag_over_index']:
                self.state['drag_over_index'] = index
                self._update()
        except Exception as e:
            self._logger.error(f"Error handling drag over: {e}", exc_info=True)
        
    def _handle_drop(self, index: int, event: dict[str, Any]):
        """处理放置事件"""
        try:
            dragging_index = self.state['dragging_index']
            if dragging_index is not None and dragging_index != index:
                items = self.state['items']
                item = items.pop(dragging_index)
                items.insert(index, item)
                
                if self.props['on_reorder']:
                    self.props['on_reorder'](items)
                    
            self.state.update({
                'dragging_index': None,
                'drag_over_index': None
            })
            self._update()
            
        except Exception as e:
            self._logger.error(f"Error handling drop: {e}", exc_info=True)
        
    def render(self) -> Element:
        """渲染可拖放列表"""
        try:
            container = super().render()
            items = self.state['items']
            dragging_index = self.state['dragging_index']
            drag_over_index = self.state['drag_over_index']
            
            for i, item in enumerate(items):
                item_container = Element('div')
                item_container.style.add(
                    opacity="1" if i != dragging_index else "0.5",
                    transform="none" if i != drag_over_index else "translateY(8px)",
                    transition="transform 0.15s ease-in-out"
                )
                
                # 添加拖放事件监听器
                item_container.set_attribute('draggable', 'true')
                item_container.add_event_listener('dragstart', lambda e, i=i: self._handle_drag_start(i, e))
                item_container.add_event_listener('dragover', lambda e, i=i: self._handle_drag_over(i, e))
                item_container.add_event_listener('drop', lambda e, i=i: self._handle_drop(i, e))
                
                # 渲染项内容
                item_content = self.props['render_item'](item)
                item_container.append_child(item_content.render())
                
                container.append_child(item_container)
                
            return container
            
        except Exception as e:
            self._logger.error(f"Error rendering draggable list: {e}", exc_info=True)
            raise
