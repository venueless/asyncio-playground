import os, sys
import asyncio
import traceback
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import orjson
from . import db
from .action_handlers import action_handlers
from .world import World

import logging
fmt = logging.Formatter(
    fmt="%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
sh = logging.StreamHandler(sys.stdout)
sh.setLevel(logging.DEBUG)
sh.setFormatter(fmt)

# will print debug sql
logger_db_client = logging.getLogger("tortoise.db_client")
logger_db_client.setLevel(logging.DEBUG)
logger_db_client.addHandler(sh)

app = FastAPI()
worlds = {}
workers = []

@app.on_event("startup")
async def startup_event():
    await asyncio.sleep(1)
    await db.init()
    world = World("load-test")
    await world.load()
    worlds[world.id] = world

@app.on_event("shutdown")
async def shutdown_event():
    pass

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    workers.append(websocket)
    try:
        while True:
            message = orjson.loads(await websocket.receive_text())
            async def handle_message():
                try:
                    world = worlds[message[0]] # TODO handle non-existing world
                    handler = action_handlers[message[1]]
                    result = await handler(world, message[3])
                    response = ["success", message[2], result, {"broadcast_name": getattr(handler, "broadcast_name", None)}]
                except Exception as e:
                    traceback.print_exc()
                    response = ["error", message[2], str(e)]
                await websocket.send_text(orjson.dumps(response, default=db.json_default).decode())

            asyncio.create_task(handle_message())
    except WebSocketDisconnect:
        workers.remove(websocket)
