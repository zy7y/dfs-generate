import threading

import uvicorn
import webview

import socket
import random

from main import app


def get_unused_port():
    """获取未被使用的端口"""
    while True:
        port = random.randint(1024, 65535)  # 端口范围一般为1024-65535
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(("localhost", port))
            sock.close()
            return port
        except OSError:
            pass


def desktop_client():
    port = get_unused_port()
    t = threading.Thread(target=uvicorn.run, args=(app,), kwargs={"port": port})
    t.daemon = True
    t.start()
    webview.create_window("DFS代码生成", url=f"http://127.0.0.1:{port}")
    webview.start(debug=True)


if __name__ == "__main__":
    desktop_client()
