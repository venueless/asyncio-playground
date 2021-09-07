from tortoise.models import Model
from tortoise import fields

class World(Model):
    id = fields.CharField(max_length=50, pk=True)
    title = fields.CharField(max_length=300)
    config = fields.JSONField()
    # rooms = relationship("Room")
    # users = relationship("User")

    class Meta:
        table = "worlds"

    def __str__(self):
        return self.id

class User(Model):
    id = fields.UUIDField(pk=True)
    world = fields.ForeignKeyField('models.World', related_name='users')
    client_id = fields.CharField(max_length=200, null=True, index=True)
    token_id = fields.CharField(max_length=200, null=True, index=True)
    profile = fields.JSONField()

    class Meta:
        table = "users"
        unique_together = (("client_id", "world_id"), ("token_id", "world_id"))

    def __str__(self):
        return self.id

class Room(Model):
    id = fields.UUIDField(pk=True)
    world = fields.ForeignKeyField('models.World', related_name='rooms')
    name = fields.CharField(max_length=300)
    description = fields.TextField()
    modules = fields.JSONField()

    class Meta:
        table = "rooms"

    def __str__(self):
        return self.name

# class RoomEvent(Model):
#     id = Column(ULID, primary_key=True, default=ulid.new)
#     room = fields.ForeignKeyField('models.Room', related_name='events')
#     sender = fields.ForeignKeyField('models.User')
#     timestamp = fields.DatetimeField()
#     type = fields.CharField(max_length=64)
#     content = fields.JSONField()
#
#     class Meta:
#         table = "room_events"
#
#     def __str__(self):
#         return self.id
