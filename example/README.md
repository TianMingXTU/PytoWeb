# PytoWeb个人展示网站示例

这是一个使用PytoWeb框架创建的个人展示网站示例。展示了如何使用PytoWeb的组件系统来构建现代化的响应式网站。

## 功能特点

- 响应式设计
- 现代UI组件
- 单页面应用
- 组件化开发
- 优雅的动画效果

## 项目结构

```
example/
├── app.py              # 主应用文件
├── static/            # 静态资源
│   ├── css/          # 样式文件
│   ├── js/           # JavaScript文件
│   └── images/       # 图片资源
└── README.md         # 项目说明
```

## 运行项目

1. 确保已安装PytoWeb框架：
```bash
pip install pytoweb
```

2. 添加示例图片：
- 将你的头像保存为 `static/images/avatar.jpg`
- 将项目截图保存为 `static/images/project1.jpg`、`project2.jpg`、`project3.jpg`

3. 运行应用：
```bash
python app.py
```

4. 在浏览器中访问：`http://localhost:8000`

## 自定义内容

1. 修改个人信息：
- 编辑 `app.py` 中的文本内容
- 替换 `static/images` 中的图片

2. 调整样式：
- 修改组件中的 `style.add()` 方法参数

3. 添加新功能：
- 创建新的组件类
- 在 `HomePage` 类中添加组件

## 技术栈

- PytoWeb框架
- Python
- HTML/CSS
- 响应式设计
