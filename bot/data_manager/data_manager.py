import asyncio


from .data_fetcher import DataFetcher
from .data_persistance import DataPersistance
from .data_synthesizer import DataSynthesizer
from .data_distributor import DataDistributor


class DataManager:

    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.data_persistance = DataPersistance()
        self.data_synthesizer = DataSynthesizer()
        self.data_distributor = DataDistributor()
        self.binance_rest_configs = [
            {"mins": 15,  "interval": "1s",  "label": "1hr_1s", "symbol": "BTCUSDT"},
            {"mins": 1440, "interval": "1m",  "label": "1day_1m", "symbol": "BTCUSDT"},
            {"mins": 1440, "interval": "15m", "label": "1day_15m", "symbol": "BTCUSDT"}
        ]
        self.binance_wss_params = ["btcusdt@kline_1m", "btcusdt@kline_1s"]

    async def handle_binance_rest_data(self):
        for config in self.binance_rest_configs:
            raw_data = await self.data_fetcher.fetch_binance_rest(
                config['mins'], config['interval'], config['symbol']
            )
            df = await self.data_synthesizer.synthesize_raw_binance_rest_data(raw_data)
            await self.data_distributor.distribute_binance_rest(
                df, config['interval'], config['label'] 
            )

    async def handle_wss_pipeline(self):
        await asyncio.gather(
            self.data_fetcher.fetch_binance_wss(
                self.binance_wss_params, self._handle_binance_wss_data
            ),
            self.data_fetcher.fetch_clob_wss(self._handle_clob_wss_data)
        )

    async def handle_persistant_15m_binance_rest(self):
        config = self.binance_rest_configs[2]

        while True:
            df = await self.data_persistance.persistantly_get_binance_rest( 15, config['interval'], config['symbol'])
            
            if df is not None:
                await self.data_distributor.distribute_persistant_binance_rest(df, config['interval'], config['label'])
                print(f"🔄 Boss Updated: {config['label']} sync complete.")

            await asyncio.sleep(1)

    async def _handle_binance_wss_data(self, msg):
        if 'k' not in msg:
            if 'result' in msg:
                print("🚀 Subscription successful, waiting for first candle...")
            return 
        kline = msg['k']
        if kline.get('x'): 
            df = await self.data_synthesizer.synthesize_raw_binance_wss_data(msg)
            if df is not None:
                interval = kline.get('i')
                await self.data_distributor.distribute_binance_wss(df=df, interval=interval)

    async def _handle_clob_wss_data(self, msg):
        pass






async def main():
    pass

if __name__ == "__main__":
    asyncio.run(main())

