binance_rest_config = [
            {"mins": 15,  "interval": "1s",  "label": "1hr_1s", "symbol": "BTCUSDT"},
            {"mins": 1440, "interval": "1m",  "label": "1day_1m", "symbol": "BTCUSDT"},
            {"mins": 1440, "interval": "15m", "label": "1day_15m", "symbol": "BTCUSDT"}
]

binance_wss_config = ["btcusdt@kline_1m", "btcusdt@kline_1s"]