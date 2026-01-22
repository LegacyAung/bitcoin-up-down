from dataclasses import dataclass, asdict

@dataclass
class Candle:
    timestamp:int
    open:float
    high:float
    low:float
    close:float
    volume:float


@dataclass
class MacdSchema:
    timestamp:int
    close:float
    macd_line:float
    signal_line:float
    histogram:float