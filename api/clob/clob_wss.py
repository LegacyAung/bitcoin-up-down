import asyncio
from config import CLOB_WEBSOCKET
from ..websocket_services import WebsocketService



class ClobWss:
    def __init__(self, channel_type, sub_msg_payload, condition_id, callback):

        self.channel_type = channel_type.lower()
        self.sub_msg_payload = sub_msg_payload
        self.condition_id = condition_id
        self.callback = callback
        self.wss_url = f"{CLOB_WEBSOCKET}/ws/{self.channel_type}" 

        
        self.task = None

        
        self.service = WebsocketService(
            url = self.wss_url,
            payload = self.sub_msg_payload,
            callback = self.callback
        )

    async def connect_clob_wss(self):
        """Starts the service in the background and returns the task."""
        if self.task and not self.task.done():
            return self.task
        print(f"📡 Starting CLOB {self.channel_type} for {self.condition_id}...")
        self.task = asyncio.create_task(self.service.connect())
        return self.task

    
    async def disconnect_clob_wss(self):
        """Uses your WebsocketService methods to shut down cleanly."""
        if not self.task:
            return
        self.service.stop()
        await self.service.disconnect()
        if not self.task.done():
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        print(f"✅ {self.condition_id} fully disconnected.")





# class ClobWss:
#     def __init__(
#             self,
#             channel_type: str,
#             sub_msg_payload: dict,
#             condition_id: str,
#             callback: callable
#         ):
        
#         self.channel_type = channel_type.lower()
#         self.sub_msg_payload = sub_msg_payload
#         self.condition_id = condition_id
#         self.callback = callback

#         self.wss_url = f"{CLOB_WEBSOCKET}/ws/{self.channel_type}" 

#         self.is_running = False
#         self.active_connections = {}
        
        

#         self.service = WebsocketService(
#             url = self.wss_url,
#             payload = self.sub_msg_payload,
#             callback = self.callback
#         )

#     async def connect_clob_wss(self):
#         self.is_running = True
#         if self.condition_id in self.active_connections:
#             print(f"⚠️ {self.condition_id} is already running.")
#             return

#         print(f"📡 Starting CLOB {self.channel_type} for {self.condition_id}...")
#         task = asyncio.create_task(self.service.connect())
#         self.active_connections[self.condition_id] = task
#         try:
#             await task
#         except asyncio.CancelledError:
#             print(f"🛑 Task for {self.condition_id} was cancelled.")
#         finally:
#             self.active_connections.pop(self.condition_id, None)

#     async def disconnect_clob_wss(self, condition_id):
#         if condition_id in self.active_connections:
#             self.service.stop()
#             task = self.active_connections.get(condition_id)
#             if task:
#                 task.disconnect()
#                 try:
#                     await task
#                 except asyncio.CancelledError:
#                     print(f"✅ {self.condition_id} task fully cleaned up.")
#             self.active_connections.pop(self.condition_id, None)




if __name__ == "__main__":
    
    async def main():
        pass