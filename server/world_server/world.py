import json # for loading the world config file
import uuid
from . import db
from .room import Room

class World:
    def __init__(self, id):
        self.id = id
        self.world = None
        self.users = None
        self.users_by_id = None
        self.users_by_client_id = None
        self.rooms = None
        self.rooms_by_id = None

    async def load(self):
        async with db.pool.acquire() as con, con.transaction():
            world = await con.fetchrow("""
                SELECT *
                FROM worlds
                WHERE worlds.id = $1
            """, self.id)
            if world:
                rooms = await con.fetch("""
                    SELECT id, name, description, modules
                    FROM rooms
                    WHERE rooms.world_id = $1
                """, self.id)
                self.rooms = [Room(room) for room in rooms]
                self.users = []
            else:
                print("world does not exist, loading from file")
                # load file sync, we don't care at startup
                with open("world-load-test.json") as f:
                    world_config = json.load(f)
                world = world_config["world"]
                self.rooms = []
                self.users = []
                await con.execute("""
                    INSERT INTO worlds(id, title, config)
                    VALUES ($1, $2, $3::json)
                """, world["id"], world["title"], {})

                for room in world_config["rooms"]:
                    room["id"] = uuid.uuid4()
                    await con.execute("""
                        INSERT INTO rooms(id, name, description, modules, world_id)
                        VALUES ($1, $2, $3, $4::json, $5)
                    """, room["id"], room["name"], room["description"], room["modules"], world["id"])
                    self.rooms.append(Room(room))
        self.world = world
        self.users_by_id = {user.id: user for user in self.users}
        self.users_by_client_id = {user.client_id: user for user in self.users}
        self.rooms_by_id = {str(room.id): room for room in self.rooms}


    async def authenticate_user(self, login_info):
        user = self.users_by_client_id.get(login_info["client_id"], None)
        if not user:
            user = {
                "id": uuid.uuid4(),
                "client_id": login_info["client_id"],
                "profile": {}
            }
            async with db.pool.acquire() as con, con.transaction():
                await con.execute("""
                    INSERT INTO users(id, client_id, profile, world_id)
                    VALUES ($1, $2, $3::json, $4)
                """, user["id"], user["client_id"], user["profile"], self.id)
            self.users.append(user)
            self.users_by_id[str(user["id"])] = user
            self.users_by_client_id[user["client_id"]] = user
        return {
            "world.config": {
                "title": self.world["title"],
                "rooms": self.rooms
            },
            "user": user
        }
