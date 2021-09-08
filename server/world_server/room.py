from datetime import datetime
import ulid
from . import db

class Room:
    def __init__(self, dbRoom):
        self.id = dbRoom["id"]
        self.name =  dbRoom["name"]
        self.description = dbRoom["description"]
        self.modules = dbRoom["modules"]
        self.events = []

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "modules": self.modules
        }

    async def create_event(self, data):
        event = {
            "id": ulid.new(),
            "room_id": self.id,
            "sender_id": data["sender_id"],
            "timestamp": datetime.now(),
            "type": data["type"],
            "content": data["content"],
        }
        async with db.pool.acquire() as con, con.transaction():
            await con.execute("""
                INSERT INTO room_events(id, room_id, sender_id, timestamp, type, content)
                VALUES ($1, $2, $3, $4, $5, $6::json)
            """, event["id"], event["room_id"], event["sender_id"], event["timestamp"], event["type"], event["content"])
            self.events.append(event)
        return event
