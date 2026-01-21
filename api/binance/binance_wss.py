import asyncio
import json
from config import BINANCE_WEBSOCKET
from .binance_service import BinanceService



class BinanceWss:
    def __init__(self):

        self.binance_websocket=BINANCE_WEBSOCKET
        self.binance_service=BinanceService()

        # state management
        self.is_running = False
        self.last_callback = None


    async def stream_binance_data(self, params, callback):
        self.last_callback = callback
        self.is_running = True
        subscribe_msg = {
            "method":"SUBSCRIBE",
            "params":params, #["btcusdt@kline_1m"]
            "id":1
        }
        print(f"🚀 Streaming Binance 1m Candles")
        try:
            await self.binance_service.stream_binance_wss(
                self.binance_websocket,
                subscribe_msg=subscribe_msg,
                callback=callback
            )
        except Exception as e:
            print(e)

            

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