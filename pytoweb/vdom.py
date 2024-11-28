"""Virtual DOM implementation for PytoWeb."""
from typing import Dict, List, Optional, Any
import difflib

class VNode:
    """Virtual DOM Node."""
    def __init__(self, tag: str, props: Dict = None, children: List = None):
        self.tag = tag
        self.props = props or {}
        self.children = children or []
        self.key = props.get('key') if props else None
        
    def __eq__(self, other):
        if not isinstance(other, VNode):
            return False
        return (self.tag == other.tag and 
                self.props == other.props and 
                self.children == other.children)

class VDOMDiffer:
    """Handles virtual DOM diffing and patching."""
    
    @staticmethod
    def diff(old_node: Optional[VNode], new_node: Optional[VNode]) -> List[Dict]:
        """Generate a list of patches based on differences between nodes."""
        patches = []
        
        if old_node is None:
            patches.append({
                'type': 'CREATE',
                'node': new_node
            })
        elif new_node is None:
            patches.append({
                'type': 'REMOVE'
            })
        elif old_node != new_node:
            if old_node.tag != new_node.tag:
                patches.append({
                    'type': 'REPLACE',
                    'node': new_node
                })
            else:
                # Props diff
                props_patch = VDOMDiffer._diff_props(old_node.props, new_node.props)
                if props_patch:
                    patches.append({
                        'type': 'PROPS',
                        'props': props_patch
                    })
                
                # Children diff
                children_patches = VDOMDiffer._diff_children(
                    old_node.children,
                    new_node.children
                )
                patches.extend(children_patches)
        
        return patches
    
    @staticmethod
    def _diff_props(old_props: Dict, new_props: Dict) -> Optional[Dict]:
        """Compare props and return differences."""
        props_patch = {}
        
        # Check for changed or new props
        for key, value in new_props.items():
            if key not in old_props or old_props[key] != value:
                props_patch[key] = value
                
        # Check for removed props
        for key in old_props:
            if key not in new_props:
                props_patch[key] = None
                
        return props_patch if props_patch else None
    
    @staticmethod
    def _diff_children(old_children: List[VNode], new_children: List[VNode]) -> List[Dict]:
        """Compare children nodes and return patches."""
        patches = []
        
        # Use difflib for optimal diff
        matcher = difflib.SequenceMatcher(None, old_children, new_children)
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                for i in range(i1, i2):
                    patches.append({
                        'type': 'REPLACE_CHILD',
                        'index': i,
                        'node': new_children[j1 + (i - i1)] if i - i1 < j2 - j1 else None
                    })
            elif tag == 'delete':
                for i in range(i1, i2):
                    patches.append({
                        'type': 'REMOVE_CHILD',
                        'index': i
                    })
            elif tag == 'insert':
                for j in range(j1, j2):
                    patches.append({
                        'type': 'INSERT_CHILD',
                        'index': j,
                        'node': new_children[j]
                    })
                    
        return patches

class VDOMRenderer:
    """Handles rendering virtual DOM to real DOM."""
    _string_pool = {}
    _pool_size = 1000
    
    @staticmethod
    def _get_pooled_string(s: str) -> str:
        if s not in VDOMRenderer._string_pool:
            if len(VDOMRenderer._string_pool) >= VDOMRenderer._pool_size:
                VDOMRenderer._string_pool.clear()
            VDOMRenderer._string_pool[s] = s
        return VDOMRenderer._string_pool[s]
    
    @staticmethod
    def create_element(vnode: VNode) -> str:
        if isinstance(vnode, str):
            return VDOMRenderer._get_pooled_string(vnode)
            
        void_elements = {
            'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
            'link', 'meta', 'param', 'source', 'track', 'wbr'
        }
        
        tag = VDOMRenderer._get_pooled_string(vnode.tag)
        html = ['<{}'.format(tag)]
        
        if vnode.props:
            props_str = VDOMRenderer._props_to_string(vnode.props)
            html.append(VDOMRenderer._get_pooled_string(props_str))
            
        if tag in void_elements:
            html.append('/>')
            return VDOMRenderer._get_pooled_string(''.join(html))
            
        html.append('>')
        
        if vnode.children:
            for child in vnode.children:
                if isinstance(child, VNode):
                    html.append(VDOMRenderer.create_element(child))
                else:
                    html.append(str(child))
                    
        html.append('</{}>'.format(tag))
        return VDOMRenderer._get_pooled_string(''.join(html))
    
    @staticmethod
    def _props_to_string(props: Dict) -> str:
        """Convert props dictionary to HTML attributes string."""
        if not props:
            return ''
            
        attributes = []
        for key, value in props.items():
            if value is None or value is False:
                continue
            if value is True:
                attributes.append(key)
            else:
                # 处理事件处理器
                if key.startswith('on'):
                    # 将Python函数转换为JavaScript事件处理器
                    value = "pytoWeb.handleEvent('{}', this)".format(key)
                # 处理样式对象
                elif key == 'style' and isinstance(value, dict):
                    value = ';'.join('{}:{}'.format(k, v) for k, v in value.items())
                # 处理类名列表
                elif key == 'class' and isinstance(value, (list, set)):
                    value = ' '.join(value)
                    
                attributes.append('{}="{}"'.format(key, str(value).replace('"', "&quot;")))
                
        return ' ' + ' '.join(attributes) if attributes else ''

    @staticmethod
    def render_to_string(vnode: Any) -> str:
        """Render a virtual DOM node to HTML string."""
        try:
            if isinstance(vnode, (str, int, float)):
                return str(vnode)
            elif isinstance(vnode, VNode):
                return VDOMRenderer.create_element(vnode)
            elif hasattr(vnode, 'render'):
                # Handle components that have a render method
                rendered = vnode.render()
                return VDOMRenderer.render_to_string(rendered)
            elif isinstance(vnode, (list, tuple)):
                # Handle lists of nodes
                return ''.join(VDOMRenderer.render_to_string(child) for child in vnode)
            else:
                return str(vnode)
        except Exception as e:
            raise Exception(f"Failed to render node: {e}")
