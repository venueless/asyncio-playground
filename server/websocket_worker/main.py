import asyncio
import traceback
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import orjson
from .world_client import WorldClient
from .action_handlers import action_handlers

WORLD_URL = 'ws://world_server:8375/ws'

app = FastAPI()
world_client = None
clients = []

@app.on_event("startup")
async def startup_event():
    global world_client
    world_client = WorldClient(WORLD_URL)
    world_client.register_message_callback(handle_message)
    await world_client.connect()

@app.on_event("shutdown")
async def shutdown_event():
    await world_client.close()

async def handle_message(message):
    print(message)

@app.websocket("/ws/world/{world}/")
async def websocket_endpoint(websocket: WebSocket, world: str):
    await websocket.accept()
    # first message must be auth
    auth_message = orjson.loads(await websocket.receive_text())
    if auth_message[0] != "authenticate":
        await websocket.close()
        return
    (data, options) = await world_client.call(world, "authenticate_user", auth_message[1])
    user = data["user"]
    await websocket.send_text(orjson.dumps(["authenticated", {
        "world.config": data["world.config"], # needs to be filtered for user permissions
        "user.config": user
    }]).decode())
    client = {
        "user": user,
        "websocket": websocket,
        "room": None
    }
    clients.append(client)
    try:
        while True:
            message = orjson.loads(await websocket.receive_text())
            if message[0] == "ping":
                await websocket.send_text(orjson.dumps(["pong", message[1]]).decode())
                continue
            async def handle_message():
                try:
                    handler = action_handlers[message[0]]
                    result = await handler(client, message[2], world, world_client, clients)
                    response = ["success", message[1], result]
                except Exception as e:
                    traceback.print_exc()
                    response = ["error", message[1], str(e)]
                await websocket.send_text(orjson.dumps(response).decode())
            asyncio.create_task(handle_message())
    except WebSocketDisconnect:
        clients.remove(client)
