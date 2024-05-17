from fastapi import FastAPI
from router import aerich
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(title="DFS - FastAPI SQLModel CRUD",
              description='''
[![](https://img.shields.io/github/stars/zy7y/dfs-generate)](https://github.com/zy7y/dfs-generate)
[![](https://img.shields.io/github/forks/zy7y/dfs-generate)](https://github.com/zy7y/dfs-generate)
[![](https://img.shields.io/github/repo-size/zy7y/dfs-generate?style=social)](https://github.com/zy7y/dfs-generate)
[![](https://img.shields.io/github/license/zy7y/dfs-generate)](https://gitee.com/zy7y/dfs-generate/blob/master/LICENSE)

支持ORM：[SQLModel](https://sqlmodel.tiangolo.com/)、[Tortoise ORM](https://tortoise.github.io/)

支持前端: [Vue](https://cn.vuejs.org/)
''')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(aerich)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", reload=True, port=5000)
