"""
Server module for PytoWeb
"""

from __future__ import annotations
from typing import Dict, Any, Optional, Callable, List
import logging
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import mimetypes
import json
from urllib.parse import parse_qs, urlparse
import http

class ServerError(Exception):
    """Server error"""
    pass

class RequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler"""
    
    def do_GET(self) -> None:
        """Handle GET request"""
        try:
            # Parse URL
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query = parse_qs(parsed_url.query)
            
            print(f"[DEBUG] Handling GET request for path: {path}")
            print(f"[DEBUG] Available routes: {list(self.server.routes.keys())}")
            
            # Find route handler
            handler = self.server.routes.get(path)
            if handler:
                try:
                    print(f"[DEBUG] Found handler for path: {path}")
                    # Call route handler
                    response = handler({"query": query, "method": "GET"})
                    if response:
                        print(f"[DEBUG] Handler returned response: {response[:200]}...")
                        self.send_response(http.HTTPStatus.OK)
                        self.send_header('Content-type', 'text/html; charset=utf-8')
                        self.end_headers()
                        self.wfile.write(response.encode('utf-8'))
                    else:
                        print("[DEBUG] Handler returned None")
                        self.send_error(http.HTTPStatus.INTERNAL_SERVER_ERROR, "Handler returned None")
                except Exception as e:
                    print(f"[DEBUG] Error in route handler: {e}")
                    self._log_error(f"Error in route handler: {e}")
                    self.send_error(http.HTTPStatus.INTERNAL_SERVER_ERROR)
            else:
                print(f"[DEBUG] No handler found for path: {path}")
                # Try to serve static file
                static_file = os.path.join(self.server.static_dir, path.lstrip('/'))
                print(f"[DEBUG] Looking for static file: {static_file}")
                if os.path.exists(static_file) and os.path.isfile(static_file):
                    print(f"[DEBUG] Found static file: {static_file}")
                    self.serve_static_file(static_file)
                else:
                    print(f"[DEBUG] Static file not found: {static_file}")
                    # Return 404
                    self.send_error(http.HTTPStatus.NOT_FOUND)
        except Exception as e:
            print(f"[DEBUG] Error handling GET request: {e}")
            self._log_error(f"Error handling GET request: {e}")
            self.send_error(http.HTTPStatus.INTERNAL_SERVER_ERROR)
            
    def do_POST(self) -> None:
        """Handle POST request"""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(post_data) if post_data else {}
            except json.JSONDecodeError:
                data = parse_qs(post_data)
            
            # Find route handler
            handler = self.server.routes.get(self.path)
            if handler:
                try:
                    # Call route handler
                    response = handler({"data": data, "method": "POST"})
                    if response:
                        self.send_response(http.HTTPStatus.OK)
                        self.send_header('Content-type', 'text/html; charset=utf-8')
                        self.end_headers()
                        self.wfile.write(response.encode('utf-8'))
                    else:
                        self.send_error(http.HTTPStatus.INTERNAL_SERVER_ERROR, "Handler returned None")
                except Exception as e:
                    self._log_error(f"Error in route handler: {e}")
                    self.send_error(http.HTTPStatus.INTERNAL_SERVER_ERROR)
            else:
                self.send_error(http.HTTPStatus.NOT_FOUND)
        except Exception as e:
            self._log_error(f"Error handling POST request: {e}")
            self.send_error(http.HTTPStatus.INTERNAL_SERVER_ERROR)
            
    def serve_static_file(self, filepath: str) -> None:
        """Serve static file"""
        try:
            # Get file MIME type
            content_type = self.guess_type(filepath)
                
            # Read file content
            with open(filepath, 'rb') as f:
                content = f.read()
                
            # Send response
            self.send_response(http.HTTPStatus.OK)
            self.send_header('Content-type', content_type)
            self.send_header('Content-length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self._log_error(f"Error serving static file: {e}")
            self.send_error(http.HTTPStatus.INTERNAL_SERVER_ERROR)
            
    def guess_type(self, filepath: str) -> str:
        """Guess file MIME type"""
        content_type, _ = mimetypes.guess_type(filepath)
        return content_type or 'application/octet-stream'
        
    def _log_error(self, message: str) -> None:
        """Log error"""
        logging.error(f"{message}\n{traceback.format_exc()}")

class Server(HTTPServer):
    """PytoWeb server class"""
    
    def __init__(self, host: str = "localhost", port: int = 8000):
        """Initialize server"""
        super().__init__((host, port), RequestHandler)
        self.routes: Dict[str, Callable] = {}
        self.middleware: List[Callable] = []
        self.static_dir = os.path.join(os.getcwd(), "static")
        self._logger = logging.getLogger(__name__)
        
        # Create static file directory
        if not os.path.exists(self.static_dir):
            os.makedirs(self.static_dir)
            
    def add_route(self, path: str, handler: Callable[..., Any]) -> None:
        """Add route handler"""
        print(f"[DEBUG] Adding route: {path}")
        if not path.startswith('/'):
            path = '/' + path
        self.routes[path] = handler
        print(f"[DEBUG] Current routes: {list(self.routes.keys())}")
    
    def use(self, middleware: Callable[..., Any]) -> None:
        """Add middleware"""
        self.middleware.append(middleware)
    
    def run(self, host: str, port: int) -> None:
        """Run HTTP server"""
        try:
            print(f"[DEBUG] Starting server at http://{host}:{port}")
            print(f"[DEBUG] Available routes: {list(self.routes.keys())}")
            self.serve_forever()
        except Exception as e:
            raise ServerError(f"Failed to start server: {e}") from e

    def handle_error(self, request: Any, client_address: Any) -> None:
        """Handle request error"""
        self._logger.error(f"Error handling request from {client_address}:\n{traceback.format_exc()}")
