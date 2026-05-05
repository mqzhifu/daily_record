#!/usr/bin/env python3
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from datetime import datetime
import socket

class LoggingHTTPRequestHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        """自定义日志格式，输出详细的HTTP请求信息"""
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        client_ip = self.client_address[0]
        method = self.command
        path = self.path
        protocol = self.request_version
        status_code = args[0] if args else '-'
        log_line = f"[{now}] {client_ip} - {method} {path} {protocol} -> {status_code}"
        print(log_line)
    
    def do_GET(self):
        """处理GET请求，输出请求信息"""
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        client_ip = self.client_address[0]
        print(f"[{now}] [GET] {client_ip} 请求: {self.path}")
        try:
            super().do_GET()
        except Exception:
            # 捕获所有异常，静默处理
            pass
    
    def do_POST(self):
        """处理POST请求，输出请求信息"""
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        client_ip = self.client_address[0]
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b''
        print(f"[{now}] [POST] {client_ip} 请求: {self.path}")
        print(f"[{now}] [POST] Content-Length: {content_length}")
        if content_length > 0 and content_length < 1024:
            try:
                print(f"[{now}] [POST] Body: {body.decode('utf-8')}")
            except:
                print(f"[{now}] [POST] Body: (binary data)")
        try:
            super().do_POST()
        except Exception:
            # 捕获所有异常，静默处理
            pass
    
    def do_OPTIONS(self):
        """处理OPTIONS请求，输出请求信息"""
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        client_ip = self.client_address[0]
        print(f"[{now}] [OPTIONS] {client_ip} 请求: {self.path}")
        try:
            super().do_OPTIONS()
        except Exception:
            # 捕获所有异常，静默处理
            pass

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
    
    print(f"==========================================")
    print(f"Web Server Started on port {port}")
    print(f"Serving files from: {front_dir}")
    print(f"Access: http://localhost:{port}")
    print(f"==========================================")
    print("Press Ctrl+C to stop")
    print("------------------------------------------")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n------------------------------------------")
        print("Server stopped.")
        httpd.server_close()

if __name__ == '__main__':
    main()
