import asyncio
import orjson
action_handlers = {}

async def broadcast(clients, ownClient, message):
    for client in clients:
        if client == ownClient:
            continue
        asyncio.create_task(client["websocket"].send_text(orjson.dumps(message).decode()))

def action(name, broadcast_name=None):
    def inner(fn):
        action_handlers[name] = fn
        if broadcast_name:
            fn.broadcast_name = broadcast_name
        return fn
    return inner

@action("user.update")
async def user_update(client, update, world, world_client, clients):
    (user, options) = await world_client.call(world, "user.update", {
        "id": client["user"]["id"],
        "update": update
    })
    client["user"] = user
    return user

@action("user.fetch")
async def user_fetch(client, data, world, world_client, clients):
    (payload, options) = await world_client.call(world, "user.fetch", {
        "ids": data["ids"]
    })
    return payload

@action("room.subscribe")
async def room_subscribe(client, data, world, world_client, clients):
    (payload, options) = await world_client.call(world, "room.subscribe", {
        "user_id": client["user"]["id"],
        "room_id": data["room"]
    })
    client["room"] = data["room"]
    return payload

@action("room.send")
async def room_send(client, data, world, world_client, clients):
    (payload, options) = await world_client.call(world, "room.send", {
        "sender_id": client["user"]["id"],
        "room_id": data["room"],
        "type": data["type"],
        "content": data["content"]
    })
    await broadcast(clients, client, ["room.event", payload])
    return payload

@action("room.fetch")
async def room_fetch(client, data, world, world_client, clients):
    (payload, options) = await world_client.call(world, "room.fetch", {
        "room_id": data["room"],
        "before_id": data["before_id"],
        "count": data["count"]
    })
    return payload
