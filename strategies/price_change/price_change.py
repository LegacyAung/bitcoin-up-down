import json
import pandas as pd

from bot.global_state import state


class PriceChange:

    def __init__(self, data, bound_loads):
        self.data = data
        self.bound_loads = bound_loads

        self._user_channel_ts = state.user_channel_ts
        self._rolling_timestamps = state.rolling_timestamps

    async def current_yes_ask_price(self):
        return await self._get_dynamic_price('yes', 'best_ask', 'current')
            

    async def current_no_ask_price(self):
        return await self._get_dynamic_price('no', 'best_ask', 'current')
    
    async def current_yes_bid_price(self):
        return await self._get_dynamic_price('yes', 'best_bid', 'current')

    async def current_no_bid_price(self):
        return await self._get_dynamic_price('no', 'best_bid', 'current')

    async def next_yes_ask_price(self):
        return await self._get_dynamic_price('yes', 'best_ask', 'next')

    async def next_no_ask_price(self):
        return await self._get_dynamic_price('no', 'best_ask', 'next')

    async def next_yes_bid_price(self):
        return await self._get_dynamic_price('yes', 'best_bid', 'next')

    async def next_no_bid_price(self):
        return await self._get_dynamic_price('no', 'best_bid', 'next')


    async def _get_dynamic_price(self, side_outcome, price_type, window):
        """
        side_outcome: 'yes' (index 0) or 'no' (index 1)
        price_type: 'best_ask' or 'best_bid'
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

        sub_msg = self.bound_loads.get('sub_msg', {})
        clob_ids_raw = sub_msg.get('clob_ids')
        clob_ids = json.loads(clob_ids_raw) if isinstance(clob_ids_raw, str) else clob_ids_raw
        
        idx = 0 if side_outcome.lower() == 'yes' else 1
        target_clob_id = clob_ids[idx]

        changes_list = self.data.iloc[0].get('price_changes', [])
            
        for change_obj in changes_list:
            if change_obj.get('asset_id') == target_clob_id:
                price = change_obj.get(price_type)
                print(f"🎯 {window.upper()} {side_outcome.upper()} {price_type}: {price}")
                return price
        
        return None