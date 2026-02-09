import asyncio

from .time_manager.time_manager import TimeManager
from .market_manager2 import MarketManager

class Initiator:
    def __init__(self, work_hrs):
        self.time_manager = TimeManager()
        self.market_manager = MarketManager()

        
        self.is_running = False
        self.work_duration = work_hrs
        self.start_ts_utc = None
        self.end_ts_utc = None
        self.current_ts_utc = None

    async def start(self):

        self.start_ts_utc = self.time_manager.get_current_ts_utc()
        self.end_ts_utc = self.time_manager.get_end_ts_utc(self.start_ts_utc,self.work_duration)
        
        await self.market_manager.market_starter()
        try:
            while True:
                self.current_ts_utc = self.time_manager.get_current_ts_utc()
                if self.current_ts_utc >= self.end_ts_utc:
                    print(f"\n\n⏰ WORK HOURS REACHED: {self.current_ts_utc} >= {self.end_ts_utc}")
                    break

                self.is_running = True
                await asyncio.sleep(1)
                
        finally:
            await self.shutdown()

    async def shutdown(self):
        
        self.is_running = False
        print("\n🧹 Executing Master Cleanup...")
        await self.market_manager.market_disconnector()
        print("✅ All systems offline. Safe to exit.")


if __name__ == "__main__":
    initiator = Initiator(1)
    asyncio.run(initiator.start())