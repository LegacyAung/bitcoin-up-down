import asyncio
import json

from datetime import datetime
from api.clob.clob_rest import ClobRest
from .portfolio import Portfolio
from states.portfolio_state import portfolio_states
from states.global_state import state

class PortfolioManagerTest:

    def __init__(self, stats_file, clob_rest):
        self.clob_rest = clob_rest
        self.portfolio =  Portfolio(self.clob_rest)
        self.gs = state
        self.pf_states = portfolio_states

        # --- Bankroll Configuration ---
        self.total_bankroll = 1000.0        # Total account value
        self.operational_limit = 200.0      # Active risk cap
        self.max_legs = 4                   # 3 Active + 1 Emergency
        self.slot_size = self.operational_limit / self.max_legs


        # --- Performance Tracking Settings ---
        self.stats_file = stats_file
        self.history = []                   # List of 1s (win) and 0s (loss)
        self.seed_p = 0.55                  # Day 1 "Guess" win rate
        self.min_sample_size = 20           # Trades needed to trust live data
        self.rolling_window = 100           # Keep only recent 100 trades

        # --- states ---
        self.active_trades = []             # Tracks open positions {slug_ts: data}


        # Auto-load historical data on startup
        self.load_state()

    # --- 1. WIN RATE LOGIC (The "p" in Kelly) ---
    @property
    def current_win_rate(self): 
        """Calculates p by blending seed data with live data for safety."""

        count = len(self.history)
        if count == 0:
            return self.seed_p
        
        live_p = sum(self.history) / count

        if count < self.min_sample_size:
            weight = count / self.min_sample_size
            return (live_p * weight) + (self.seed_p * (1 - weight))
        
        return live_p
    

    async def get_trade_approval(self, entry_price):
        """
        DecisionMaker calls this to see if a trade is allowed.
        Returns a dict (Approval Metadata) or None.
        """

        
    async def _update_balance_from_clob(self):
        """Parses the raw balance string into a float."""
        if not self.clob_rest : return

        raw_balance_dict = await self.portfolio.get_balance(asset_type="COLLATERAL") 
        raw_balance = raw_balance_dict.get('balance')
        self.total_bankroll = float(raw_balance)/ 1000000
        print(f"💰 Wallet Synchronized: ${self.total_bankroll:.2f}")

    
    async def _track_track_current_open_orders(self):
        """
        Takes your 'unfulfilled order' JSON structure and tracks it.
        Uses the 'market' key as the unique ID for settlement.
        """
        if not self.clob_rest : return

        current_slug_ts = self.gs.rolling_timestamps.get('current')

        events_meta = self.gs.events_metadata

        if len(events_meta) <= 0 : return

        all_open_orders = []

        for e in events_meta:
            if e.get('timestamp') == current_slug_ts:

                order_params = {
                    'order_id': None,
                    'market_id': e.get('condition_id'),
                    'asset_id': None
                }
                open_orders = await self.portfolio.get_order_positions(order_params)
                
                all_open_orders.extend(open_orders)
        print(f"all the open orders: for current market: {all_open_orders}")
        return all_open_orders    

        

    async def _track_current_active_trades(self):
        """
        Takes your 'fulfilled order' JSON structure and tracks it.
        Uses the 'market' key as the unique ID for settlement.
        """
        if not self.clob_rest : return

        current_slug_ts = self.gs.rolling_timestamps.get('current')

        events_meta = self.gs.events_metadata

        if len(events_meta) <= 0 : return

        all_confirmed_trades = []

        for e in events_meta:
            if e.get('timestamp') == current_slug_ts:
                
                trade_params = {
                    'order_id':None,
                    'maker_address':None,
                    'market_id':e.get('condition_id'),
                    'asset_id': None
                }

                active_trades = await self.portfolio.get_active_positions(trade_params)
            
                all_confirmed_trades.extend(active_trades)

        print(f"all the active trades: for current market: {all_confirmed_trades}")
        return all_confirmed_trades

    
    # --- 2. SIZING ENGINE ---
    def cal_trade_size(self, entry_price: float):
        """Calculates USD amount using Half-Kelly on a $50 slot."""
        if entry_price <= 0 or entry_price >= 1.0:
            return 0.0
        

        p = self.current_win_rate
        q = 1 - p
        b = (1.0 - entry_price) / entry_price  # Odds (Reward/Risk)

        #Kelly formula version A f = p - (q/b)
        f_star = p - (q/b)

        # No edge = No trade
        if f_star <= 0:
            return 0.0
        
        multiplier = 0.25 if len(self.history) < self.min_sample_size else 0.5
        applied_fraction = f_star * multiplier

        final_usd = self.slot_size * applied_fraction

        return round(min(final_usd, self.slot_size), 2)
    
    # --- 3. TRADE MANAGEMENT ---
    def record_entry(self, slug_ts, side, price, size_usd):

        self.active_trades[slug_ts] = {
            "side": side,
            "entry_price": price,
            "size_usd": size_usd,
            "timestamp": datetime.now().isoformat()
        }

        print(f"📡 [ENTRY] {side} at {price} | Size: ${size_usd} | Timestamp_Slug: {slug_ts}")



    def settle_trade(self, slug_ts, final_price, barrier_price):
        """Determines win/loss and updates performance history."""
        pass



    # --- 4. PERSISTENCE (JSON) ---
    def save_state(self):
        """Writes performance to disk."""
        data = {
            "history": self.history,
            "updated_at": datetime.now().isoformat()
        }

        try:
            with open(self.stats_file, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"❌ Error saving portfolio: {e}")


    




if __name__ == "__main__":
    async def main():
        # 1. Initialize the REST client
        clob_rest = ClobRest()
        
        # 2. Authenticate (This is required before any L2 calls)
        await clob_rest.authenticate()
        
        portfolio_manager = PortfolioManagerTest(clob_rest)

        await portfolio_manager._cal_balance()

        
    

    asyncio.run(main())