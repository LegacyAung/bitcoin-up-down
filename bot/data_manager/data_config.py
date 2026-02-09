from dataclasses import dataclass, field
from typing import List

@dataclass
class RestConfig:
    mins: int
    interval: str
    label: str
    symbol: str = "BTCUSDT"

@dataclass
class MarketConfig:
    # Rest API Configurations
    binance_rest: List[RestConfig] = field(default_factory=lambda: [
        RestConfig(mins=15,   interval="1s",  label="1hr_1s"),
        RestConfig(mins=1440, interval="1m",  label="1day_1m"),
        RestConfig(mins=1440, interval="15m", label="1day_15m"),
    ])

    # WebSocket Channels
    binance_wss: List[str] = field(default_factory=lambda: [
        "btcusdt@kline_1m", 
        "btcusdt@kline_1s"
    ])
    
    clob_wss: List[str] = field(default_factory=lambda: [
        "book", "price_change", "last_trade_price", "best_bid_ask",
        "tick_size_change", "new_market", "market_resolved"
    ])

# Usage
config = MarketConfig()
print(config.binance_rest[0].label) # No more ['label'] keys!