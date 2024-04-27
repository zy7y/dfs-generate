from tortoise import Model, fields


class Aerich(Model):
    id = fields.IntField(pk=True)
    version = fields.CharField(max_length=255)
    app = fields.CharField(max_length=100)
    content = fields.JSONField()
