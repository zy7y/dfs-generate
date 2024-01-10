import platform

import yapf_third_party

params = [
    '--windowed',
    '--onefile',
    '--add-data', 'static:static',
    '--add-data', f'{yapf_third_party.__file__.replace("__init__.py", "")}:yapf_third_party',
    '--clean',
    '--noconfirm',
    'client.py',
]

current_os = platform.system()

from PyInstaller import __main__ as pyi

params.append("--icon"),
if current_os == "Windows":
    params.append("static/logo.icns")
    path = "./dist/client.exe"
else:
    params.append("static/logo.icon")
    path = "./dist/client"

pyi.run(params)
print(path)