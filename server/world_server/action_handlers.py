action_handlers = {}

def action(name, broadcast_name=None):
    def inner(fn):
        action_handlers[name] = fn
        if broadcast_name:
            fn.broadcast_name = broadcast_name
        return fn
    return inner

@action("authenticate_user")
async def user_update(world, login_info):
    return await world.authenticate_user(login_info)

@action("user.update")
async def user_update(world, data):
    user = world.users_by_id[data["id"]]
    user.update(data["update"])
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
