action_handlers = {}

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
async def user_fetch():
    pass

@action("room.subscribe")
async def room_subscribe():
    pass

@action("room.send")
async def room_send():
    pass

@action("room.fetch")
async def room_fetch():
    pass
