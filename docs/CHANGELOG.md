# Change Log
## Release v0.2.5  (2024-05-17)
- #62 每次打开应用时自动打开配置窗口
- #63 mysql断开链接后接口返回错误信息
- #64 兼容主键列名非id时dao层引发的错误

## Release v0.2.4  (2024-05-12)
- #59 简化pywebview桌面端构建
- #58 将curd修改为crud

## Release v0.2.3  (2024-05-02)
- #50 api.ts 请求头参数位置错误
- #52 调整单测、接入覆盖率CI
- #55 crud.ts 列名未小驼峰导致错误

## Release v0.2.2  (2024-05-01)
- #28 基于[fast-crud](http://fast-crud.docmirror.cn/)生成`Vue`代码完整管理页面操作
- #41 使用create-dmg完成macos安装包制作
- #42 客户端打包时机CI调整为发版时
- #47 生成模型指向实际表名，防止找不到表的错误

## Release v0.2.1  (2024-04-28)
- #35 修复Windows桌面端运行报错
- #34 增加源码运行说明

## Release v0.2.0 （2024-04-27）
- #30 支持Tortoise ORM 代码生成
- #27 移除依赖`FastAPI`,`SQLAlchemy`,`Pydantic`,`Uvicorn`, `Jinja2`...
- 优化目录结构

## Release v0.1.x (2023-12 ~ 2023-04-27)
- 支持SQLModel
- 生成FastAPI接口`详情查询`,`更新`,`新增`,`删除`,`分页查询`