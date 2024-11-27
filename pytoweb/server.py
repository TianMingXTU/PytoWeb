"""
PytoWeb服务器模块
"""

from typing import Optional, Dict, Callable, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import logging
import traceback
from urllib.parse import parse_qs, urlparse
import os

class RequestHandler(BaseHTTPRequestHandler):
    """HTTP请求处理器"""
    
    def do_GET(self):
        """处理GET请求"""
        try:
            # 解析URL
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query = parse_qs(parsed_url.query)
            
            # 查找路由处理器
            handler = self.server.routes.get(path)
            if handler:
                # 调用路由处理器
                response = handler({"query": query, "method": "GET"})
                if response:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(response.encode('utf-8'))
                else:
                    self.send_error(500, "Handler returned None")
            else:
                # 尝试提供静态文件
                static_file = os.path.join(self.server.static_dir, path.lstrip('/'))
                if os.path.exists(static_file) and os.path.isfile(static_file):
                    self.serve_static_file(static_file)
                else:
                    # 返回404
                    self.send_error(404)
        except Exception as e:
            logging.error(f"Error handling GET request: {e}\n{traceback.format_exc()}")
            self.send_error(500)
            
    def do_POST(self):
        """处理POST请求"""
        try:
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(post_data) if post_data else {}
            except json.JSONDecodeError:
                data = parse_qs(post_data)
            
            # 查找路由处理器
            handler = self.server.routes.get(self.path)
            if handler:
                # 调用路由处理器
                response = handler({"data": data, "method": "POST"})
                if response:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(response.encode('utf-8'))
                else:
                    self.send_error(500, "Handler returned None")
            else:
                self.send_error(404)
        except Exception as e:
            logging.error(f"Error handling POST request: {e}\n{traceback.format_exc()}")
            self.send_error(500)
            
    def serve_static_file(self, filepath: str):
        """提供静态文件"""
        try:
            # 获取文件MIME类型
            content_type = self.guess_type(filepath)
                
            # 读取文件内容
            with open(filepath, 'rb') as f:
                content = f.read()
                
            # 发送响应
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.send_header('Content-length', len(content))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            logging.error(f"Error serving static file: {e}\n{traceback.format_exc()}")
            self.send_error(500)
            
    def guess_type(self, filepath: str) -> str:
        """猜测文件MIME类型"""
        ext = os.path.splitext(filepath)[1].lower()
        return {
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.json': 'application/json',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
        }.get(ext, 'application/octet-stream')

class Server(HTTPServer):
    """PytoWeb服务器类"""
    
    def __init__(self, host: str = "localhost", port: int = 8000):
        super().__init__((host, port), RequestHandler)
        self.routes: Dict[str, Callable] = {}
        self.middleware = []
        self.static_dir = os.path.join(os.getcwd(), "static")
        self._logger = logging.getLogger(__name__)
        
        # 创建静态文件目录
        if not os.path.exists(self.static_dir):
            os.makedirs(self.static_dir)
        
    def add_route(self, path: str, handler: Callable):
        """添加路由处理器"""
        self.routes[path] = handler
        
    def use(self, middleware: Any):
        """添加中间件"""
        self.middleware.append(middleware)
        
    def run(self, host: str = "localhost", port: int = 8000):
        """运行服务器"""
        self.server_name = host
        self.server_port = port
        
        try:
            self.serve_forever()
        except KeyboardInterrupt:
            self._logger.info("Server stopped by user")
        except Exception as e:
            self._logger.error(f"Server error: {e}\n{traceback.format_exc()}")
            raise
        finally:
            self.server_close()
