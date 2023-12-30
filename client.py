import subprocess
import time

import webview

import socket
import random


def get_unused_port():
    """获取未被使用的端口"""
    while True:
        port = random.randint(1024, 65535)  # 端口范围一般为1024-65535
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('localhost', port))
            sock.close()
            return port
        except OSError:
            pass


def desktop_client():
    port = get_unused_port()
    p = subprocess.Popen(f"uvicorn main:app --port {port}", shell=True)
    webview.create_window("DFS代码生成", url=f"http://127.0.0.1:{port}")
    time.sleep(1)
    webview.start(debug=True)
    p.kill()


if __name__ == '__main__':
    desktop_client()
