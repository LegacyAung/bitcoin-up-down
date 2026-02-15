import asyncio
import json
import time
import websockets

from websockets.exceptions import ConnectionClosed


class WebsocketService:

    def __init__(self, url, payload, callback, ping_int=5, timeout=5):
        """
        Universal WebSocket Service
        :param url: The WSS endpoint.
        :param payload: The subscription JSON.
        :param callback: Async function to process data.
        """
        
        self.url = url
        self.payload = payload
        self.callback = callback
        self.ping_int = ping_int
        self.timeout = timeout

        self.connected_event = asyncio.Event()
        self.is_running = False
        self.last_msg_time = 0
        self._retry_delay = 1
        self.max_retry_delay = 60
        self._ws = None

    async def _health_check(self, ws):
        try:
            while self.is_running:
                await asyncio.sleep(5)
                if time.time() - self.last_msg_time > self.ping_int:
                    try:
                        await ws.send("ping") 
                        await ws.ping()
                    except Exception as e:
                        print(f"🚨 [HEALTH] {self.url} stale. Forcing reconnection...")
                        await self.disconnect()
                        break
        except asyncio.CancelledError:
            pass
    
    async def connect(self):

        self.is_running = True

        while self.is_running:
            monitor_task = None
            try:
                async with websockets.connect(
                        self.url, 
                        ping_interval=self.ping_int, 
                        ping_timeout=self.timeout
                    ) as ws:
                    self._ws = ws
                    self.connected_event.set()
                    self.last_msg_time = time.time()
                    self._retry_delay = 1

                    monitor_task = asyncio.create_task(self._health_check(self._ws))

                    await ws.send(json.dumps(self.payload))
                    print(f"✅ Connected to {self.url}")


                    async for message in ws:
                        self.last_msg_time = time.time()

                        if message == "ping":
                            await ws.send("pong")
                            continue
                        
                        try:
                            data = json.loads(message)
                            await self.callback(data)

                        except json.JSONDecodeError:
                            pass

            except (ConnectionClosed, Exception) as e:
                if self.is_running:
                    self.connected_event.clear()
                    print(f"❌ Connection error on {self.url}: {e}")
                    await self.reconnect()
                else:
                    break

            finally:
                if monitor_task and not monitor_task.done():
                    monitor_task.cancel()
                    try:
                        await monitor_task
                    except asyncio.CancelledError:
                        pass
                self._ws = None
    
    async def reconnect(self):
        print(f"⏳ Retrying {self.url} in {self._retry_delay}s...")
        await asyncio.sleep(self._retry_delay)
        self._retry_delay = min(self._retry_delay * 2, self.max_retry_delay)
    
    async def disconnect(self):
        if self._ws:
            await self._ws.close()
            self._ws = None
            
    def stop(self):
        self.is_running = False
        print(f"🛑 Stopping service for {self.url}")
