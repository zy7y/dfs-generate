import platform
import subprocess

import yapf_third_party
from PyInstaller import __main__ as pyi


def gen_client_py():
    code = """
import random
import socket
import threading

from dfs_generate.server import app


def get_unused_port():
    while True:
        port = random.randint(1024, 65535)  # 端口范围一般为1024-65535
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(("localhost", port))
            sock.close()
            return port
        except OSError:
            pass


import webview


def desktop_client():
    port = get_unused_port()
    t = threading.Thread(target=app.run, kwargs={"port": port})
    t.daemon = True
    t.start()
    webview.create_window("DFS代码生成", f"http://127.0.0.1:{port}")
    webview.start()


if __name__ == '__main__':
    desktop_client()
    """
    with open("dfs_generate/client.py", "w", encoding="utf-8") as f:
        f.write(code)


gen_client_py()


params = [
    "--windowed",
    "--onefile",
    "--add-data",
    "web/dist:web/dist",
    "--add-data",
    f'{yapf_third_party.__file__.replace("__init__.py", "")}:yapf_third_party',
    "--clean",
    "--noconfirm",
    "--name=client",
    "dfs_generate/client.py",
]

pyi.run(params)


# 如果是macos，则压缩打包后的目录
if platform.system() == "Darwin":
    cmds = ["zip", "-r", "dist/client.zip", "dist/"]
    subprocess.call(cmds)
    rm_cmds = ["rm", "-rf", "dist/client.app"]
    subprocess.call(rm_cmds)
    # 删除空目录
    rm_cmds = ["rm", "-rf", "dist/client"]
    subprocess.call(rm_cmds)
