import platform

import yapf_third_party

params = [
    '--windowed',
    '--onefile',
    '--add-data', 'static:static',
    '--add-data', f'{yapf_third_party.__file__.replace("__init__.py", "")}:yapf_third_party',
    '--clean',
    '--noconfirm',
    '--icon', 'static/logo.icns',
    'client.py',
]

current_os = platform.system()

from PyInstaller import __main__ as pyi

pyi.run(params)
if current_os == "Windows":
    path = "./dist/client.exe"
else:
    path = "./dist/client"
