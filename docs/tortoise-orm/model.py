from tortoise import Model, fields


class Aerich(Model):
    aerich_id = fields.IntField(pk=True)
    version = fields.CharField(max_length=255)
    app = fields.CharField(max_length=100)
    content = fields.JSONField()

    class Meta:
        table = 'aerich'