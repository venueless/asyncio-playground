import asyncio
import orjson
from . import db

action_handlers = {}

async def broadcast(workers, ownWorker, message):
    for worker in workers:
        if worker == ownWorker:
            continue
        asyncio.create_task(worker.send_text(orjson.dumps(message, default=db.json_default).decode()))

def action(name, broadcast_name=None):
    def inner(fn):
        action_handlers[name] = fn
        if broadcast_name:
            fn.broadcast_name = broadcast_name
        return fn
    return inner

@action("authenticate_user")
async def user_update(world, login_info, worker, workers):
    return await world.authenticate_user(login_info)

@action("user.update")
async def user_update(world, data, worker, workers):
    user = world.users_by_id[data["id"]]
    user.update(data["update"])
    return user

@action("user.fetch")
async def user_fetch(world, data, worker, workers):
    return [world.users_by_id[id] for id in data["ids"]]

@action("room.subscribe")
async def room_subscribe(world, data, worker, workers):
    # TODO store subscribed users
    room = world.rooms_by_id[data["room_id"]]
    return {
        "subscribed_at_id": room.events[-1]["id"] if len(room.events) > 0 else None
    }

@action("room.send")
async def room_send(world, data, worker, workers):
    room = world.rooms_by_id[data["room_id"]]
    event = await room.create_event(data)
    await broadcast(workers, worker, ["broadcast_room", room.id, ["room.event", event]])
    return event

@action("room.fetch")
async def room_fetch(world, data, worker, workers):
    room = world.rooms_by_id[data["room_id"]]
    return room.events[-data["count"]:] # actually find by id later
