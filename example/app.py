"""
使用PytoWeb框架创建的个人展示网站示例
"""

from pytoweb.components import (
    Component, Container, Text, Image, Link, Grid,
    Flex, Card, ModernTabs, Badge, Button
)
from pytoweb.styles import Style
from pytoweb.app import App
from pytoweb.router import Router

class Header(Component):
    """页面头部组件"""
    def __init__(self):
        super().__init__()
        self.tag_name = "header"
        self.style.add(
            padding="1rem",
            background_color="#ffffff",
            box_shadow="0 2px 4px rgba(0,0,0,0.1)",
            position="sticky",
            top="0",
            z_index="100"
        )
        
        # 创建导航栏
        nav = Flex(justify="space-between", align="center")
        
        # Logo
        logo = Link("/", "John Doe")
        logo.style.add(
            font_size="1.5rem",
            font_weight="bold",
            color="#333",
            text_decoration="none"
        )
        
        # 导航链接
        nav_links = Flex(gap="2rem")
        nav_links.add_child(Link("#about", "关于我"))
        nav_links.add_child(Link("#skills", "技能"))
        nav_links.add_child(Link("#projects", "项目"))
        nav_links.add_child(Link("#contact", "联系我"))
        
        nav.add_child(logo)
        nav.add_child(nav_links)
        self.add_child(nav)

class Hero(Component):
    """首页英雄区组件"""
    def __init__(self):
        super().__init__()
        self.tag_name = "section"
        self.style.add(
            padding="4rem 2rem",
            background="linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            color="#ffffff",
            text_align="center"
        )
        
        container = Container()
        
        # 头像
        avatar = Image("/static/images/avatar.jpg", "John Doe")
        avatar.style.add(
            width="150px",
            height="150px",
            border_radius="50%",
            margin_bottom="2rem",
            border="4px solid #ffffff"
        )
        
        # 标题和简介
        title = Text("John Doe", "h1")
        title.style.add(
            font_size="3rem",
            margin_bottom="1rem"
        )
        
        subtitle = Text("全栈开发工程师", "h2")
        subtitle.style.add(
            font_size="1.5rem",
            margin_bottom="2rem",
            opacity="0.9"
        )
        
        description = Text("热爱编程，专注于Web开发和人工智能领域")
        description.style.add(
            max_width="600px",
            margin="0 auto",
            line_height="1.6"
        )
        
        container.add_child(avatar)
        container.add_child(title)
        container.add_child(subtitle)
        container.add_child(description)
        
        self.add_child(container)

class About(Component):
    """关于我组件"""
    def __init__(self):
        super().__init__()
        self.tag_name = "section"
        self.set_prop("id", "about")
        self.style.add(
            padding="4rem 2rem",
            background_color="#f8f9fa"
        )
        
        container = Container()
        
        # 标题
        title = Text("关于我", "h2")
        title.style.add(
            font_size="2.5rem",
            text_align="center",
            margin_bottom="3rem"
        )
        
        # 内容网格
        grid = Grid(columns=2, gap="2rem")
        
        # 左侧：个人简介
        bio = Card(
            title="个人简介",
            body="""
            我是一名全栈开发工程师，拥有5年的开发经验。
            热爱技术，善于学习，乐于分享。
            目前专注于Web开发和人工智能领域，致力于创造优秀的用户体验。
            """
        )
        
        # 右侧：详细信息
        details = Card(
            title="详细信息",
            body="""
            - 🎓 教育背景：计算机科学与技术
            - 💼 工作经验：5年全栈开发
            - 🌏 期望工作地：全球范围
            - 🎯 职业目标：技术专家
            """
        )
        
        grid.add_child(bio)
        grid.add_child(details)
        
        container.add_child(title)
        container.add_child(grid)
        
        self.add_child(container)

class Skills(Component):
    """技能组件"""
    def __init__(self):
        super().__init__()
        self.tag_name = "section"
        self.set_prop("id", "skills")
        self.style.add(
            padding="4rem 2rem",
            background_color="#ffffff"
        )
        
        container = Container()
        
        # 标题
        title = Text("技能专长", "h2")
        title.style.add(
            font_size="2.5rem",
            text_align="center",
            margin_bottom="3rem"
        )
        
        # 技能标签组
        skills_grid = Grid(columns=4, gap="1rem")
        
        skills = [
            ("Python", "success"),
            ("JavaScript", "success"),
            ("React", "primary"),
            ("Vue", "primary"),
            ("Node.js", "info"),
            ("Django", "info"),
            ("Docker", "warning"),
            ("Git", "warning"),
            ("AI/ML", "primary"),
            ("数据库", "info"),
            ("Linux", "warning"),
            ("敏捷开发", "success")
        ]
        
        for skill, type_ in skills:
            badge = Badge(skill, type_, True)
            badge.style.add(
                font_size="1rem",
                padding="0.5rem 1rem"
            )
            skills_grid.add_child(badge)
            
        container.add_child(title)
        container.add_child(skills_grid)
        
        self.add_child(container)

class Projects(Component):
    """项目展示组件"""
    def __init__(self):
        super().__init__()
        self.tag_name = "section"
        self.set_prop("id", "projects")
        self.style.add(
            padding="4rem 2rem",
            background_color="#f8f9fa"
        )
        
        container = Container()
        
        # 标题
        title = Text("项目展示", "h2")
        title.style.add(
            font_size="2.5rem",
            text_align="center",
            margin_bottom="3rem"
        )
        
        # 项目卡片网格
        projects_grid = Grid(columns=3, gap="2rem")
        
        projects = [
            {
                "title": "AI助手应用",
                "description": "基于深度学习的智能问答系统，支持多轮对话和知识图谱",
                "tech": ["Python", "PyTorch", "React", "Docker"],
                "image": "/static/images/project1.jpg"
            },
            {
                "title": "电商平台",
                "description": "全栈电商解决方案，包含商品管理、订单处理、支付系统等",
                "tech": ["Vue", "Node.js", "MongoDB", "Redis"],
                "image": "/static/images/project2.jpg"
            },
            {
                "title": "数据可视化平台",
                "description": "企业级数据分析和可视化平台，支持多种图表类型和实时数据",
                "tech": ["React", "D3.js", "Python", "PostgreSQL"],
                "image": "/static/images/project3.jpg"
            }
        ]
        
        for project in projects:
            card = Card()
            
            # 项目图片
            image = Image(project["image"], project["title"])
            image.style.add(
                width="100%",
                height="200px",
                object_fit="cover"
            )
            
            # 项目标题
            card_title = Text(project["title"], "h3")
            card_title.style.add(
                font_size="1.5rem",
                margin="1rem 0"
            )
            
            # 项目描述
            description = Text(project["description"])
            description.style.add(
                margin_bottom="1rem",
                color="#666"
            )
            
            # 技术标签
            tech_container = Flex(gap="0.5rem", wrap=True)
            for tech in project["tech"]:
                badge = Badge(tech, "primary", True)
                badge.style.add(
                    font_size="0.8rem"
                )
                tech_container.add_child(badge)
            
            card.add_child(image)
            card.add_child(card_title)
            card.add_child(description)
            card.add_child(tech_container)
            
            projects_grid.add_child(card)
            
        container.add_child(title)
        container.add_child(projects_grid)
        
        self.add_child(container)

class Contact(Component):
    """联系方式组件"""
    def __init__(self):
        super().__init__()
        self.tag_name = "section"
        self.set_prop("id", "contact")
        self.style.add(
            padding="4rem 2rem",
            background_color="#ffffff"
        )
        
        container = Container()
        
        # 标题
        title = Text("联系我", "h2")
        title.style.add(
            font_size="2.5rem",
            text_align="center",
            margin_bottom="3rem"
        )
        
        # 联系方式卡片
        contact_grid = Grid(columns=3, gap="2rem")
        
        contacts = [
            {
                "title": "邮箱",
                "content": "john.doe@example.com",
                "icon": "📧"
            },
            {
                "title": "GitHub",
                "content": "github.com/johndoe",
                "icon": "💻"
            },
            {
                "title": "LinkedIn",
                "content": "linkedin.com/in/johndoe",
                "icon": "👔"
            }
        ]
        
        for contact in contacts:
            card = Card()
            card.style.add(
                text_align="center",
                padding="2rem"
            )
            
            # 图标
            icon = Text(contact["icon"])
            icon.style.add(
                font_size="3rem",
                margin_bottom="1rem"
            )
            
            # 标题
            card_title = Text(contact["title"], "h3")
            card_title.style.add(
                font_size="1.5rem",
                margin_bottom="1rem"
            )
            
            # 内容
            content = Link("#", contact["content"])
            content.style.add(
                color="#666",
                text_decoration="none"
            )
            
            card.add_child(icon)
            card.add_child(card_title)
            card.add_child(content)
            
            contact_grid.add_child(card)
            
        container.add_child(title)
        container.add_child(contact_grid)
        
        self.add_child(container)

class Footer(Component):
    """页脚组件"""
    def __init__(self):
        super().__init__()
        self.tag_name = "footer"
        self.style.add(
            padding="2rem",
            background_color="#333",
            color="#ffffff",
            text_align="center"
        )
        
        text = Text("© 2024 John Doe. All rights reserved.")
        text.style.add(
            opacity="0.8"
        )
        
        self.add_child(text)

class HomePage(Component):
    """首页组件"""
    def __init__(self):
        super().__init__()
        self.add_child(Header())
        self.add_child(Hero())
        self.add_child(About())
        self.add_child(Skills())
        self.add_child(Projects())
        self.add_child(Contact())
        self.add_child(Footer())

# 创建应用实例
app = App()
router = Router()

# 注册路由
@router.route("/")
def home():
    return HomePage()

# 启动应用
if __name__ == "__main__":
    app.use(router)
    app.run(debug=True)
