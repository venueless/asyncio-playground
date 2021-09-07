import asyncio
from fastapi import FastAPI, WebSocket
import orjson
from .world_client import WorldClient

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
    print(auth_message)
    response = await world_client.call(world, "authenticate_user", auth_message[1])
    user = response["user"]
    await websocket.send_text(orjson.dumps(["authenticated", {
        "world.config": response["world.config"], # needs to be filtered for user permissions
        "user.config": user
    }]))
    client = {
        "user": {
            "id": user["id"],
            "profile": user["profile"]
        },
        "websocket": websocket
    }
    clients.append(client)
    try:
        while True:
            message = orjson.loads(await websocket.receive_text())
            if message[0] == "ping":
                await websocket.send_text(orjson.dumps(["pong", message[1]]).decode())
                continue
            asyncio.create_task(process_message)
    except WebSocketDisconnect:
        clients.remove(client)
