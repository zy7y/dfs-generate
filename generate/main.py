template = """
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html

from router import {table_name}_router

app = FastAPI()


@app.get("/docs", include_in_schema=False)
def docs():
    return get_swagger_ui_html(
        swagger_js_url="https://cdn.bootcdn.net/ajax/libs/swagger-ui/5.6.2/swagger-ui-bundle.min.js",
        swagger_css_url="https://cdn.bootcdn.net/ajax/libs/swagger-ui/5.6.2/swagger-ui.min.css"
    )


app.include_router({table_name}router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", reload=True, port=5000)

"""


def render(table_name):
    return template.format(table_name=table_name)
