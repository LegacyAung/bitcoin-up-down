import pandas as pd
from dataclasses import asdict
from ..utils.schemas import *



class DataSynthesizer:
    def __init__(self) :
        self.candle : None 

    # changing raw data from binance wss to panda dataframe
    async def synthesize_raw_binance_wss_data(self,raw_data):
        k = raw_data.get('k')
        if not k:
            return None
        self.candle = Candle(
            timestamp=int(k['t']),
            open=float(k['o']),
            high=float(k['h']),
            low=float(k['l']),
            close=float(k['c']),
            volume=float(k['v'])
        )

        df = pd.DataFrame([asdict(self.candle)]) 
        return df
    
    # changing raw data from binance rest to panda dataframe
    async def synthesize_raw_binance_rest_data(self, raw_data_list):
        if not raw_data_list:
            return pd.DataFrame()
        
        candles = []
        for item in raw_data_list:
            self.candle = Candle(
                timestamp=int(item[0]),
                open=float(item[1]),
                high=float(item[2]),
                low=float(item[3]),
                close=float(item[4]),
                volume=float(item[5])
            )
            candles.append(asdict(self.candle))
        
        return pd.DataFrame(candles)


# ---------------------------------------------- CLOB WSS Methods ------------------------------------------------##

    async def synthesize_raw_clob_wss_book(self, raw_data):
        
        bids = [OrderLevel(price=float(b['price']), size=float(b['size'])) for b in raw_data.get('bids', [])]
        asks = [OrderLevel(price=float(a['price']), size=float(a['size'])) for a in raw_data.get('asks', [])]

        book = ClobBook(
            event_type=raw_data.get('event_type'),
            asset_id=raw_data.get('asset_id'),
            market=raw_data.get('market'),
            timestamp=int(raw_data.get('timestamp')),
            bids=bids,
            asks=asks,
            hash=raw_data.get('hash')
        )

        return pd.DataFrame([asdict(book)])

    async def synthesize_raw_clob_wss_price_change(self, raw_data):
        price_changes = []
        for change in raw_data.get('price_changes', []):
            price_changes.append(PriceChangeLevel(
                asset_id=change.get('asset_id'),
                price=float(change.get('price')),
                size=float(change.get('size')),
                side=change.get('side'),
                hash=change.get('hash'),
                best_bid=float(change.get('best_bid', 0)),
                best_ask=float(change.get('best_ask', 0))
            ))

        pc = ClobPriceChange(
            event_type = raw_data.get('event_type'),
            market=raw_data.get('market'),
            timestamp=int(raw_data.get('timestamp')),
            price_changes=price_changes
        )

        return pd.DataFrame([asdict(pc)])

    async def synthesize_raw_clob_wss_last_trade_price(self, raw_data):
        ltp = ClobLastTradePrice(
            event_type=raw_data.get('event_type'),
            asset_id=raw_data.get('asset_id'),
            market=raw_data.get('market'),
            price=float(raw_data.get('price')),
            side=float(raw_data.get('size')),
            timestamp=int(raw_data.get('timestamp'))
        )
        return pd.DataFrame([asdict(ltp)])

    async def synthesize_raw_clob_wss_best_bid_ask(self, raw_data):
        bba = ClobBestBidAsk(
            event_type=raw_data.get('event_type'),
            asset_id=raw_data.get('asset_id'),
            market=raw_data.get('market'),
            best_bid=float(raw_data.get('best_bid')),
            best_ask=float(raw_data.get('best_ask')),
            spread=float(raw_data.get('spread', 0)),
            timestamp=int(raw_data.get('timestamp'))
        )
        return pd.DataFrame([asdict(bba)])

    async def synthesize_raw_clob_wss_tick_size_change(self, raw_data):
        tsc = ClobTickSizeChange(
            event_type=raw_data.get('event_type'),
            asset_id=raw_data.get('asset_id'),
            market=raw_data.get('market'),
            old_tick_size=float(raw_data.get('old_tick_size')),
            new_tick_size=float(raw_data.get('new_tick_size')),
            timestamp=int(raw_data.get('timestamp'))
        )
        return pd.DataFrame([asdict(tsc)])

    async def synthesize_raw_clob_wss_new_market(self, raw_data):
        msg = raw_data.get('event_message', {})
        event_msg = EventMessage(
            id=str(msg.get('id')),
            ticker=msg.get('ticker'),
            slug=msg.get('slug'),
            title=msg.get('title'),
            description=msg.get('description')
        )

        nm = ClobNewMarket(
            event_type=raw_data.get('event_type'),
            id=str(raw_data.get('id')),
            question=raw_data.get('question'),
            market=raw_data.get('market'),
            slug=raw_data.get('slug'),
            description=raw_data.get('description'),
            assets_ids=raw_data.get('assets_ids', []),
            outcomes=raw_data.get('outcomes', []),
            event_message=event_msg,
            timestamp=int(raw_data.get('timestamp'))
        )
        return pd.DataFrame([asdict(nm)])

    async def synthesize_raw_clob_wss_market_resolved(self, raw_data):
        msg = raw_data.get('event_message', {})
        event_msg = EventMessage(
            id=str(msg.get('id')),
            ticker=msg.get('ticker'),
            slug=msg.get('slug'),
            title=msg.get('title'),
            description=msg.get('description')
        )

        mr = ClobMarketResolved(
            event_type=raw_data.get('event_type'),
            id=str(raw_data.get('id')),
            question=raw_data.get('question'),
            market=raw_data.get('market'),
            slug=raw_data.get('slug'),
            description=raw_data.get('description'),
            assets_ids=raw_data.get('assets_ids', []),
            winning_asset_id=raw_data.get('winning_asset_id'),
            winning_outcome=raw_data.get('winning_outcome'),
            event_message=event_msg,
            timestamp=int(raw_data.get('timestamp'))
        )
        return pd.DataFrame([asdict(mr)])