import os
import asyncpg
import orjson
import ulid
import uuid

async def _init_connection(con):
    await con.set_type_codec(
        'json',
        encoder=lambda v: orjson.dumps(v).decode(),
        decoder=orjson.loads,
        schema='pg_catalog'
    )


async def init():
    global pool
    pool = await asyncpg.create_pool(
        host = os.getenv("VENUELESS_DB_HOST"),
        database = os.getenv("VENUELESS_DB_NAME"),
        user = os.getenv("VENUELESS_DB_USER"),
        password = os.getenv("VENUELESS_DB_PASS"),
        init = _init_connection,
    )
    async with pool.acquire() as con:
        await con.execute("""
            CREATE TABLE IF NOT EXISTS "worlds" (
                "id" VARCHAR(50) NOT NULL PRIMARY KEY,
                "title" VARCHAR(300) NOT NULL,
                "config" JSON NOT NULL
            );
            CREATE TABLE IF NOT EXISTS "rooms" (
                "id" UUID NOT NULL PRIMARY KEY,
                "name" VARCHAR(300) NOT NULL,
                "description" TEXT NOT NULL,
                "modules" JSON NOT NULL,
                "world_id" VARCHAR(50) NOT NULL REFERENCES "worlds" ("id") ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS "users" (
                "id" UUID NOT NULL PRIMARY KEY,
                "client_id" VARCHAR(200),
                "token_id" VARCHAR(200),
                "profile" JSON NOT NULL,
                "world_id" VARCHAR(50) NOT NULL REFERENCES "worlds" ("id") ON DELETE CASCADE,
                CONSTRAINT "uid_users_client_id_world" UNIQUE ("client_id", "world_id"),
                CONSTRAINT "uid_users_token_id_world" UNIQUE ("token_id", "world_id")
            );
            CREATE INDEX IF NOT EXISTS "idx_users_client_id" ON "users" ("client_id");
            CREATE INDEX IF NOT EXISTS "idx_users_token_id" ON "users" ("token_id");
            CREATE TABLE IF NOT EXISTS "room_events" (
                "id" UUID NOT NULL PRIMARY KEY,
                "room_id" UUID NOT NULL REFERENCES "rooms" ("id") ON DELETE CASCADE,
                "sender_id" UUID NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
                "timestamp" TIMESTAMPTZ NOT NULL,
                "type" VARCHAR(64) NOT NULL,
                "content" JSON NOT NULL
            );
        """)

def json_default(value):
    if isinstance(value, asyncpg.Record):
        return dict(value)
    if isinstance(value, asyncpg.pgproto.pgproto.UUID):
        # because orjson does not use isinstance and dies on pgproto.UUIDs
        return uuid.UUID(int=value.int)
    if isinstance(value, ulid.ULID):
        return str(value)
    if hasattr(value, "json") and callable(value.json):
        return value.json()
    raise TypeError
