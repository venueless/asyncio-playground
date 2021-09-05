import os
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy import JSON
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.future import select
from sqlalchemy.types import TypeDecorator
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import sessionmaker
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

engine = None
Session = None

async def init_db():
    global engine
    global Session
    engine = create_async_engine(
        "postgresql+asyncpg://{username}:{password}@{host}/{db}".format(
            username = os.getenv("VENUELESS_DB_USER"),
            password = os.getenv("VENUELESS_DB_PASS"),
            host = os.getenv("VENUELESS_DB_HOST"),
            db = os.getenv("VENUELESS_DB_NAME"),
        ),
        echo=True,
        pool_size=20,
        max_overflow=0,
        future=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    Session = sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
        future=True,
    )

    #     await conn.execute(
    #         t1.insert(), [{"name": "some name 1"}, {"name": "some name 2"}]
    #     )
    #
    # async with engine.connect() as conn:
    #
    #     # select a Result, which will be delivered with buffered
    #     # results
    #     result = await conn.execute(select(t1).where(t1.c.name == "some name 1"))
    #
    #     print(result.fetchall())
    #
    # # for AsyncEngine created in function scope, close and
    # # clean-up pooled connections
    # await engine.dispose()
