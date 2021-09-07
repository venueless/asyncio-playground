import os
from tortoise import Tortoise
import ulid
import uuid

Base = declarative_base()

class ULID(TypeDecorator):
    impl = UUID
    cache_ok = True

    def process_bind_param(self, value):
        if value is None:
            return value
        else:
            return uuid.UUID(bytes=value.bytes)

    def process_result_value(self, value):
        if value is None:
            return value
        else:
            return ulid.from_uuid(value)

class World(Base):
    __tablename__ = "worlds"
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    config = Column(JSON, nullable=False)
    rooms = relationship("Room")
    users = relationship("User")

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    world_id = Column(String, ForeignKey("worlds.id"), nullable=False)
    client_id = Column(String)
    token_id = Column(String)
    profile = Column(JSON, nullable=False)

Index('idx_users_world_client_id', User.world_id, User.client_id, unique=True)
Index('idx_users_world_token_id', User.world_id, User.token_id, unique=True)

class Room(Base):
    __tablename__ = "rooms"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    world_id = Column(String, ForeignKey("worlds.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    modules = Column(JSON)

class RoomEvent(Base):
    __tablename__ = "room_events"
    id = Column(ULID, primary_key=True, default=ulid.new)
    room_id = Column(UUID, ForeignKey("rooms.id"), nullable=False)
    sender_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    timestamp = DateTime(timezone=True)
    type = Column(String, nullable=False)
    content = Column(JSON)


async def init():
    await Tortoise.init(
        db_url="postgresql+asyncpg://{username}:{password}@{host}/{db}".format(
            username = os.getenv("VENUELESS_DB_USER"),
            password = os.getenv("VENUELESS_DB_PASS"),
            host = os.getenv("VENUELESS_DB_HOST"),
            db = os.getenv("VENUELESS_DB_NAME"),
        ),
        modules={"models": ["app.models"]}
    )
    # Generate the schema
    await Tortoise.generate_schemas()

async def shutdown():
    await Tortoise.close_connections()
