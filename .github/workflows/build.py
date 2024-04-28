import os.path
import platform
import subprocess

import pymysql
import yapf_third_party
from PyInstaller import __main__ as pyi

CLIENT_PY = "dfs_generate/client.py"


def build_web():
    subprocess.run("npm i", cwd="web", shell=True)
    subprocess.run("npm run build", cwd="web", shell=True)


def gen_client_py():
    code = """
import random
import socket
import threading
import sys
monkey_patch = type('MonkeyPatchSys', (object,), {'write': lambda self, *args, **kwargs: None})

if sys.stderr is None:
    sys.stderr = monkey_patch()

if sys.stdout is None:
    sys.stdout = monkey_patch()

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
    with open(CLIENT_PY, "w", encoding="utf-8") as f:
        f.write(code)


# build_web()
gen_client_py()


def get_pyinstaller_add_data_by_package(name):
    return f'{name.__file__.replace("__init__.py", "")}:{name.__name__}'


params = [
    "--windowed",
    "--onefile",
    "--add-data",
    "dfs_generate/*:.",
    "--add-data",
    get_pyinstaller_add_data_by_package(pymysql),
    "--add-data",
    get_pyinstaller_add_data_by_package(yapf_third_party),
    "--add-data",
    "web/dist:web/dist",
    "--clean",
    "--noconfirm",
    "--name=client",
    CLIENT_PY,
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

if os.path.isfile(CLIENT_PY):
    os.remove(CLIENT_PY)
