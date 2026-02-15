import asyncio
import time
import sys

from api.clob.clob_rest import ClobRest
from bot.data_manager.data_manager import DataManager



class PipeLineTest:
    def __init__(self):
        
        self.timestamps = ["1770986700", "1770987600"]
        self.channels = ["book", "price_change", "last_trade_price", "best_bid_ask"]
        self.binanace_params = ["btcusdt@kline_1m", "btcusdt@kline_1s"]
        self.binance_rest_cfg  = {"mins": 15, "interval": "1s", "label": "1hr_1s", "symbol": "BTCUSDT"}
        self.clob_channel_types = ['user', 'market']
        #state_management
        self.first_data_received: asyncio.Event()

    async def main_test(self):
        clob_rest = ClobRest()
        await clob_rest.authenticate()
        data_manager = DataManager()
        
        clob_wss_user = asyncio.create_task(data_manager.handle_clob_wss_pipeline(ts_user, 'user', clob_rest))

        while True:
            market_tasks = []
            
            wss_task = asyncio.create_task(data_manager.handle_binance_wss_pipeline())
            rest_task = asyncio.create_task(data_manager.handle_binance_rest_data())

            ts_user = self.timestamps[0]

            
            
            for ts in self.timestamps:
                clob_wss_task = asyncio.create_task(data_manager.handle_clob_wss_pipeline(ts, 'market', clob_rest))
                market_tasks.append(clob_wss_task)    

            
            print(f"\n🚀 Session started. Running for 3 minutes...")
            await self._time_count_down(3) 
            print("\n⌛ Time's up! Shutting down smoothly...")
            await data_manager.handle_disconnect_binance_wss()

            for ts in self.timestamps:
                await data_manager.handle_disconnect_clob_wss(ts)
            
            for task in [wss_task, rest_task, clob_wss_user] + market_tasks:
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

            print("✅ Cleanup complete. Restarting next cycle...")

    #--------------------Callback Helpers------------------------#
    async def _time_count_down(self,min):
        total_second = min * 60

        while total_second > 0:
            
            m, s = divmod(total_second, 60)

            timer = f"{m:02d}:{s:02d}"
            sys.stdout.write(f"\rNext action in: {timer} ")
            sys.stdout.flush()
        
            await asyncio.sleep(1)
            total_second -= 1
        
        
        return total_second
        


if __name__ == "__main__":

    async def main():
        pipeline_test = PipeLineTest()
        await pipeline_test.main_test()

    asyncio.run(main())