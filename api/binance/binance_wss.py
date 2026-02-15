import asyncio
from config import BINANCE_WEBSOCKET
from .binance_service import BinanceService
from ..websocket_services import WebsocketService


class BinanceWss:
    def __init__(self, params, callback):
        
        self.url = BINANCE_WEBSOCKET
        self.params = params
        self.sub_msg_payloads = {
            "method":"SUBSCRIBE",
            "params":self.params, #["btcusdt@kline_1m"]
            "id":1
        }
        self.callback = callback
        self.is_running = False


        self.service = WebsocketService(
            url = self.url,
            payload = self.sub_msg_payloads,
            callback = self.callback  
        )

    async def connect_binance_wss(self):
        print(f"🚀 Streaming Binance {self.params[0] and self.params[1]} Candles")
        self.is_running = True

        try:
            await self.service.connect()
        except Exception as e:
            print(e)

    async def disconnect_binance_wss(self):
        
        if self.is_running:

            try:
                self.service.disconnect()
                self.is_running = False

                print(f"🚀 Binance {self.params[0] and self.params[1]} Candles stream is closed")
            except Exception as e:
                print(e)
        else:
            print(f"Binance stream is not running")





# At the bottom of your file:
async def main():
    # 1. Initialize the class
    binance_wss = BinanceWss()
    
    # 2. Define how to handle the data
    async def handle_candle(data):
        # Binance kline data contains 'k' for the candle details
        print(data)

    # 3. Start the stream
    await binance_wss.stream_binance_data(handle_candle)
    

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Stream stopped by user.")