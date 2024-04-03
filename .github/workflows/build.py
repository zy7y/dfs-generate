import yapf_third_party

params = [
    "--windowed",
    "--onefile",
    "--add-data",
    "static:static",
    "--add-data",
    f'{yapf_third_party.__file__.replace("__init__.py", "")}:yapf_third_party',
    "--clean",
    "--noconfirm",
    "--name=client",
    "main.py",
]

from PyInstaller import __main__ as pyi

pyi.run(params)
