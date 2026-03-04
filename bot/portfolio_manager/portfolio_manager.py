import asyncio
import json

from api.clob.clob_rest import ClobRest
from .portfolio import Portfolio
from states.portfolio_state import portfolio_states
from states.global_state import state

class PortfolioManager:

    def __init__(self, clob_rest):
        self.clob_rest = clob_rest
        self.portfolio =  Portfolio(self.clob_rest)
        self.gs = state
        self.pf_states = portfolio_states

        

        # --- states ---
        self.order_positions = []           # Tracks open positions {slug_ts: data}
        self.active_trades = []             # Tracks active {slug_ts: data}


        # Dynamic trade size according to legs
        self._fulfilled_legs_metadata = {
            'leg_1': {
                'order_id': None,
                'trader_side':None,         # "TAKER" or "MAKER"
                'outcome': None,            # "Up" or "Down"
                'price': None,              # "Up" or "Down"
                'fee_rate_bps': None,       # Usually is 1000
                'size' : None,              # Usually is 1000    
                'total_investment': None
            },  
            'leg_2': {},
            'leg_3': {},
            'leg_4': {}
        }

        # Dynamic 
        self._unfulfilled_legs_metadata = {

        }

    async def call_portfolio(self):
        pass


    async def _portfolio_caller(self):
        """Calling all the methods from portfolio file update the wallet states"""
        if not self.clob_rest : return

        current_slug_ts = self.gs.rolling_timestamps.get('current')

        events_meta = self.gs.events_metadata

        if len(events_meta) <= 0 : return

        """Calling get_balance"""

        raw_balance_dict = await self.portfolio.get_balance(asset_type="COLLATERAL") 
        raw_balance = raw_balance_dict.get('balance')
        self.total_bankroll = float(raw_balance)/ 1000000

        """Calling get_order_positions"""
        """Calling get_active_positions"""

        for e in events_meta:
            if e.get('timestamp') == current_slug_ts:

                order_params = {
                    'order_id': None,
                    'market_id': e.get('condition_id'),
                    'asset_id': None
                }

                trade_params = {
                    'order_id':None,
                    'maker_address':None,
                    'market_id':e.get('condition_id'),
                    'asset_id': None
                }

                open_orders = await self.portfolio.get_order_positions(order_params)
                active_trades = await self.portfolio.get_active_positions(trade_params)
                
                self.order_positions.extend(open_orders)
                self.active_trades.extend(active_trades)

        

    async def _trade_approval_handler(self, entry_prices):
        """Handling trade approval states that is passed down from decision maker"""
        pass
    
    def _cal_trade_size_limit_order(self, entry_price):

        if self.pf_states.max_legs == 4:
            print(f"trade size for 1st leg...")
        
        if self.pf_states.max_legs == 3:
            print(f"trade size for 2nd leg...")

        if self.pf_states.max_legs == 2:
            print(f"trade size for 3rd leg...")

        if self.pf_states.max_legs == 1:
            print(f"trade size for 4th leg...(emergency round)")

        if self.pf_states.max_legs == 0:
            print(f"you have exceeded max legs, wait for next resolution")

    def _cal_trade_size_next_leg(self):
        pass
#------------------------------------------------helpers-----------------------------------------------------#



if __name__ == "__main__":
    async def main():
        # 1. Initialize the REST client
        clob_rest = ClobRest()
        
        # 2. Authenticate (This is required before any L2 calls)
        await clob_rest.authenticate()
        
        portfolio_manager = PortfolioManager(clob_rest)

        pass
        

        
    

    asyncio.run(main())