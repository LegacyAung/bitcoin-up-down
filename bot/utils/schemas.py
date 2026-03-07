from dataclasses import dataclass, field
from typing import List,Optional

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


#-----------------------CLOB Schemas------------------------#    

@dataclass
class OrderLevel:
    price: float
    size: float


@dataclass
class PriceChangeLevel:
    asset_id: str
    price: float
    size: float
    side: str
    hash: str
    best_bid: float
    best_ask: float

@dataclass
class EventMessage:
    id: str
    ticker: str
    slug: str
    title: str
    description: str

@dataclass
class ClobBook:
    event_type: str
    asset_id: str
    market: str
    timestamp: int
    bids: List[OrderLevel]
    asks: List[OrderLevel]
    hash: str

@dataclass
class ClobPriceChange:
    event_type: str
    market: str
    timestamp: int
    price_changes: List[PriceChangeLevel]

@dataclass
class ClobLastTradePrice:
    event_type: str
    asset_id: str
    market: str
    price: float
    side: str
    timestamp: int
    size: float = 0.0

@dataclass
class ClobBestBidAsk:
    event_type: str
    asset_id: str
    market: str
    best_bid: float
    best_ask: float
    spread: float
    timestamp: int

@dataclass
class ClobTickSizeChange:
    event_type: str
    asset_id: str
    market: str
    old_tick_size: float
    new_tick_size: float
    timestamp: int

@dataclass
class ClobNewMarket:
    event_type: str
    id: str
    question: str
    market: str
    slug: str
    description: str
    assets_ids: List[str]
    outcomes: List[str]
    event_message: EventMessage
    timestamp: int

@dataclass
class ClobMarketResolved:
    event_type: str
    id: str
    question: str
    market: str
    slug: str
    description: str
    assets_ids: List[str]
    winning_asset_id: str
    winning_outcome: str
    event_message: EventMessage
    timestamp: int


#----------------------- CLOB Schemas User Channel ------------------------# 
@dataclass
class MakerOrders:
    asset_id: str
    matched_amount: str
    order_id: str
    outcome: str
    owner: str
    price: str  

@dataclass
class ClobTrade:
    asset_id: str
    event_type: str
    id: str
    last_update: str
    maker_orders: List[MakerOrders]
    market: str
    matchtime: str
    outcome: str
    owner: str
    price: str
    side: str
    status: str
    taker_order_id: str
    timestamp: str
    trade_owner: str
    type: str    

@dataclass
class ClobOrder:
    asset_id: str
    associate_trades: str
    event_type: str
    id: str
    market: str
    order_owner: str
    original_size: str
    outcome: str
    owner: str
    price: str
    side: str
    size_matched: str
    timestamp: str
    type: str