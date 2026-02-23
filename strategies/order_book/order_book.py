import json
from bot.states.global_state import state

class OrderBook:
    def __init__(self, data, bound_loads):
        self.data = data
        self.bound_loads = bound_loads

        self._user_channel_ts = state.user_channel_ts
        self._rolling_timestamps = state.rolling_timestamps
        
    async def current_yes_ask_book(self):
        return await self._get_dynamic_book('yes', 'ask', 'current')

    async def current_no_ask_book(self):
        return await self._get_dynamic_book('no', 'ask', 'current')

    async def current_yes_bid_book(self):
        return await self._get_dynamic_book('yes', 'bid', 'current')

    async def current_no_bid_book(self):
        return await self._get_dynamic_book('no', 'bid', 'current')

    async def next_yes_ask_book(self):
        return await self._get_dynamic_book('yes', 'ask', 'next')

    async def next_no_ask_book(self):
        return await self._get_dynamic_book('no', 'ask', 'next')

    async def next_yes_bid_book(self):
        return await self._get_dynamic_book('yes', 'bid', 'next')

    async def next_no_bid_book(self):
        return await self._get_dynamic_book('no', 'bid', 'next')


    async def _get_dynamic_book(self, side_outcome, price_type, window):
        """
        side_outcome: 'yes' (index 0) or 'no' (index 1)
        price_type: 'ask' or 'bid'
        window: 'current' or 'next'
        """

        if self.data is None or (hasattr(self.data, 'empty') and self.data.empty) or len(self.data) == 0:
            return None
        if not self.bound_loads:
            return None
        
        target_ts = state.rolling_timestamps.get(window)
        incoming_ts = self.bound_loads.get('slug_timestamp')

        if target_ts != incoming_ts:
            return None

        raw_incoming_asset_id = self.data.get('asset_id')
        if hasattr(raw_incoming_asset_id, 'iloc'):
            current_asset_id = str(raw_incoming_asset_id.iloc[0]).strip()    
        else:
            current_asset_id = str(raw_incoming_asset_id).strip()

        sub_msg = self.bound_loads.get('sub_msg', {})
        clob_ids_raw = sub_msg.get('clob_ids')
        clob_ids = json.loads(clob_ids_raw) if isinstance(clob_ids_raw, str) else clob_ids_raw

        idx = 0 if side_outcome.lower() == 'yes' else 1
        target_clob_id = str(clob_ids[idx]).strip()

        if current_asset_id != target_clob_id:
            return None
        
        side = 'bids' if 'bid' in price_type else 'asks'
        raw_book = self.data.get(side, [])
        book_list = raw_book.iloc[0] if hasattr(raw_book,'iloc') else raw_book 
        
        if len(book_list) > 0 :
            print(f"🎯 {window.upper()} {side_outcome.upper()} {price_type}s: {book_list}")
            return {
                "side": side_outcome,
                "timestamp": target_ts,
                "window": window,
                "price_type": price_type,
                "book_list": book_list
            }
        
        else:
            
            return None
        
