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


import webview
webview.create_window("DFS代码生成", app)
webview.start()
    """
    with open(CLIENT_PY, "w", encoding="utf-8") as f:
        f.write(code)


build_web()
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
    CWD = "dist"
    subprocess.call(["npm", "i", "-g", "create-dmg"])
    subprocess.call(["create-dmg", "client.app"], cwd=CWD)
    subprocess.call(["rm", "-rf", "client.app", "client"], cwd=CWD)
    subprocess.call(["mv", "client 0.0.0.dmg", "client.dmg"], cwd=CWD)

if os.path.isfile(CLIENT_PY):
    os.remove(CLIENT_PY)
