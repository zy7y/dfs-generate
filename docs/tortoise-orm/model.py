from tortoise import Model, fields


class SysMenu(Model):
    id = fields.IntField(description="主键", pk=True)
    status = fields.SmallIntField(default=1, description="状态 1有效 9 删除 5选中")
    created = fields.DatetimeField(null=True,
                                   description="创建时间",
                                   auto_now_add=True)
    modified = fields.DatetimeField(null=True,
                                    description="更新时间",
                                    auto_now=True)
    name = fields.CharField(null=True, max_length=20, description="名称")
    icon = fields.CharField(null=True, max_length=100, description="菜单图标")
    path = fields.CharField(null=True, max_length=128, description="菜单url")
    type = fields.SmallIntField(description="菜单类型 0目录 1组件 2按钮 3数据", index=True)
    component = fields.CharField(null=True, max_length=128, description="组件地址")
    pid = fields.IntField(null=True, description="父id")
    identifier = fields.CharField(null=True,
                                  max_length=30,
                                  description="权限标识 user:add")
    api = fields.CharField(null=True, max_length=128, description="接口地址")
    method = fields.CharField(null=True, max_length=10, description="接口请求方式")

    class Meta:
        table = 'sys_menu'
