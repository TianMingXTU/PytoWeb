from setuptools import setup, find_packages

setup(
    name="pytoweb",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'watchdog>=2.1.0',    # 用于热重载
        'websockets>=10.0',    # 用于事件系统
        'psutil>=5.8.0',      # 用于性能监控
        'aiohttp>=3.8.0',     # 用于HTTP服务器
        'jinja2>=3.0.0',      # 用于模板渲染
        'uvicorn>=0.15.0',    # 用于ASGI服务器
        'typing-extensions>=4.0.0',  # 用于类型提示
        'python-multipart>=0.0.5',   # 用于文件上传
    ],
    extras_require={
        'dev': [
            'pytest>=6.0.0',
            'pytest-asyncio>=0.15.0',
            'pytest-cov>=2.12.0',
            'black>=21.5b2',
            'mypy>=0.900',
            'isort>=5.9.0',
        ],
        'docs': [
            'sphinx>=4.0.0',
            'sphinx-rtd-theme>=0.5.0',
            'sphinx-autodoc-typehints>=1.12.0',
        ]
    },
    author="PytoWeb Team",
    author_email="example@example.com",
    description="A Python library for creating web interfaces using pure Python",
    long_description=open("docs/README.md", encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pytoweb",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Framework :: AsyncIO",
        "Framework :: aiohttp",
    ],
    python_requires=">=3.7",
    keywords="web, ui, framework, python, html, css, javascript, virtual dom, components",
    project_urls={
        'Documentation': 'https://pytoweb.readthedocs.io/',
        'Source': 'https://github.com/yourusername/pytoweb',
        'Tracker': 'https://github.com/yourusername/pytoweb/issues',
    },
)
