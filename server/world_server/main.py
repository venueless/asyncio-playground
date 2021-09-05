from fastapi import FastAPI, WebSocket
import json # for loading the world config file
import orjson
from .action_handlers import action_handlers
from . import db
from sqlalchemy.future import select

app = FastAPI()
workers = set()

@app.on_event("startup")
async def startup_event():
    # load test world
    await db.init_db()
    async with db.Session() as session, session.begin():
        world = (await session.execute(
            select(db.World)
            .join(db.World.rooms)
            .join(db.World.users)
            .where(db.World.id == "load-test")
        )).one_or_none()
        if not world:
            # load file sync, we don't care at startup
            with open("world-load-test.json") as f:
                world_config = json.load(f)
            world = db.World(**world_config["world"], config=world_config["world"], rooms=[db.Room(**room) for room in world_config["rooms"]])
            session.add(world)
            await session.commit()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, world: str):
    await websocket.accept()
    workers.add(websocket)
    try:
        while True:
            message = orjson.loads(await websocket.receive_text())
            async def handle_message():
                response
                try:
                    handler = action_handlers[message[0]]
                    result = await handler(message[2])
                    response = ["success", message[1], result, {broadcast_name: handler.broadcast_name}]
                except Exception as e:
                    response = ["error", message[1], str(e)]
                websocket.send_text(orjson.dumps(response).decode())

            asyncio.create_task(handle_message())
    except WebSocketDisconnect:
        workers.discard(websocket)
