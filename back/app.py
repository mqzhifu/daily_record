#!/usr/bin/env python3
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from datetime import datetime

class LoggingHTTPRequestHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        """自定义日志格式，输出更详细的HTTP请求信息"""
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        client_ip = self.client_address[0]
        method = self.command
        path = self.path
        protocol = self.request_version
        status_code = args[0] if args else '-'
        log_line = f"[{now}] {client_ip} - {method} {path} {protocol} -> {status_code}"
        print(log_line)

def main():
    # 设置前端目录路径
    front_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'front')
    
    if not os.path.exists(front_dir):
        print(f"Error: Front directory not found at {front_dir}", file=sys.stderr)
        sys.exit(1)
    
    # 切换到前端目录
    os.chdir(front_dir)
    
    # 配置服务器，监听所有网络接口
    port = 90
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, LoggingHTTPRequestHandler)
    
    print(f"Web Server Started on port {port}")
    print(f"Serving files from: {front_dir}")
    print(f"Access: http://localhost:{port}")
    print("Press Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.server_close()

if __name__ == '__main__':
    main()
