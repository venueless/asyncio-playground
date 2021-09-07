import json # for loading the world config file
from . import models

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
        world = await models.World.get_or_none(id=self.id).prefetch_related("users", "rooms")
        if not world:
            print("world does not exist, loading from file")
            # load file sync, we don't care at startup
            with open("world-load-test.json") as f:
                world_config = json.load(f)
            world = await models.World.create(**world_config["world"], config=world_config["world"])
            await world.fetch_related("users", "rooms")
            for roomConfig in world_config["rooms"]:
                room = await models.Room.create(**roomConfig, world=world)
                # hack to add created room to world
                world.rooms.related_objects.append(room)


        self.world = world
        self.users = world.users.related_objects
        self.users_by_id = {user.id: user for user in self.users}
        self.users_by_client_id = {user.client_id: user for user in self.users}
        self.rooms = world.rooms.related_objects

    async def authenticate_user(self, login_info):
        user = self.users_by_client_id.get(login_info["client_id"], None)
        if not user:
            user = await models.User.create(
                client_id=login_info["client_id"],
                world=self.world,
                profile={},
            )
            self.users.append(user)
            self.users_by_id[user.id] = user
            self.users_by_client_id[user.client_id] = user
        return {
            "world.config": {
                "title": self.world.title,
                "rooms": self.rooms
            },
            "user": user
        }
