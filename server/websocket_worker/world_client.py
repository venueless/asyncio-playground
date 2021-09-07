# should we have a single connection for all worlds, or one per world?
import asyncio
import websockets
import orjson

class APIError(Exception):
    pass

class WorldClient:
    def __init__(self, url):
        self._websocket = None
        self._url = url
        self._open_requests = {}
        self._next_correlation_id = 1
        self._message_callbacks = []

    async def connect(self):
        while not self._websocket:
            try:
                self._websocket = await websockets.connect(self._url)
            except ConnectionRefusedError:
                print('World server not responsing, retrying')
                await asyncio.sleep(1)
        asyncio.create_task(self._receiveMessages())

    def register_message_callback(self, cb):
        self._message_callbacks.append(cb)

    async def call(self, world_id, action, data):
        id = self._next_correlation_id
        self._next_correlation_id += 1
        future = asyncio.get_running_loop().create_future()
        self._open_requests[id] = future
        await self._send([
            world_id,
            action,
            id,
            data
        ])
        return await future

    async def _send(self, message):
        await self._websocket.send(orjson.dumps(message).decode())

    async def _receiveMessages(self):
        try:
            while True:
                message = orjson.loads(await self._websocket.recv())
                print(message)
                if message[0] == "success" or message[0] == "error":
                    future = self._open_requests.pop(message[1]) # TODO handle missing id
                    if message[0] == "success":
                        future.set_result({data: message[2], options: message[3]})
                    else:
                        future.set_exception(APIError(message[2]))
                else:
                    for cb in self._message_callbacks:
                        asyncio.create_task(cb(message))
        except:
            # reconnect
            self._websocket = None
            await self.connect()
