import asyncio
import traceback
import orjson
from .world_client import WorldClient
from .action_handlers import action_handlers
from channels.generic.websocket import AsyncWebsocketConsumer

WORLD_URL = 'ws://world_server:8375/ws'

world_client = None
world_config = None
clients = []

# no clue where django channels startup code should go
async def startup_event():
    global world_client
    global world_config
    if world_client:
        return
    world_client = WorldClient(WORLD_URL)
    world_client.register_message_callback(handle_message)
    await world_client.connect()
    (world_config, options) = await world_client.call("load-test", "get_world_config", None)

async def handle_message(message):
    if (message[0] == "broadcast_room"):
        for client in clients:
            if client["room"] == message[1]:
                asyncio.create_task(client.send(text_data=orjson.dumps(message[2]).decode()))
    else:
        print('UNHANDLED MESSAGE', message)

class VenuelessConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.world = self.scope['url_route']['kwargs']['world']
        await startup_event()
        await self.accept()

    async def disconnect(self, close_code):
        clients.remove(self)

    async def receive(self, text_data):
        message = orjson.loads(text_data)
        if message[0] == "ping":
            await self.send(text_data=orjson.dumps(["pong", message[1]]).decode())
            return
        if message[0] == "authenticate":
            (data, options) = await world_client.call(self.world, "authenticate_user", message[1])
            user = data["user"]
            await self.send(text_data=orjson.dumps(["authenticated", {
                "world.config": world_config, # needs to be filtered for user permissions
                "user.config": user
            }]).decode())
            self.user = user
            self.room = None
            clients.append(self)
            return
        try:
            handler = action_handlers[message[0]]
            result = await handler(self, message[2], self.world, world_client, clients)
            response = ["success", message[1], result]
        except Exception as e:
            traceback.print_exc()
            response = ["error", message[1], str(e)]
        await self.send(text_data=orjson.dumps(response).decode())
