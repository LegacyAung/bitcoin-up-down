import asyncio
import json

from api.clob.clob_rest import ClobRest
from .portfolio import Portfolio
from ..executor import Execution
from ..states.portfolio_state import portfolio_states
from ..states.global_state import state



class PortfolioManager:

    def __init__(self, clob_rest):

        self.clob_rest = clob_rest
        self.portfolio =  Portfolio(self.clob_rest)
        self.execution = Execution(self.clob_rest)

        self.gs = state
        self.pf_states = portfolio_states

        

    
    async def start_portfolio(self):
       await asyncio.gather(
           self._handle_trade_intent(),
           self._observe_trade(),
        )

    async def _portfolio_caller(self):
        """Calling all the methods from portfolio file update the wallet states"""
        if not self.clob_rest : return

        """Calling get_balance"""

        raw_balance_dict = await self.portfolio.get_balance(asset_type="COLLATERAL") 
        raw_balance = raw_balance_dict.get('balance')
        total_bankroll = float(raw_balance)/ 1000000

        self.pf_states.set_wallet_balance(total_bankroll)
    
    async def _observe_trade(self):

        while True:
            await self.pf_states._update_active_trade_event.wait()
            trades = self.pf_states.active_trades
            count = len(trades)

            #Leg 1
            if count == 1:
                trade_data = trades[0]
                outcome = trade_data.get('outcome')

                self.pf_states.set_prev_leg_outcome(outcome)
                self.pf_states.set_pending(False)
                self.pf_states.increment_leg()

                operational_bal = self.pf_states.operational_balance
                investment_cost = self._cal_investment_cost()
                updated_operational_bal = operational_bal - investment_cost
                self.pf_states.set_operational_balance(updated_operational_bal)
                
                if self.pf_states.prev_leg_outcome is None: return
                price,size = self._cal_limit_order()
                next_outcome = 'Up' if self.pf_states.prev_leg_outcome == "Down" else 'Down'
                order_type = 'limit_order'
                self._process_order(next_outcome, order_type, size, price)

            #Leg 2
            if count == 2:
                pass


            #Leg 3
            if count == 3:
                pass

            #Leg 4
            if count == 4:
                pass


    async def _handle_trade_intent(self):
        """Handling trade approval states that is passed down from decision maker"""
        intent = await self.pf_states.trade_queue.get()
        print(f"got the trade intent from decision maker {intent}")
        await self._process_trade(intent)
        self.pf_states.trade_queue.task_done()


    async def _process_trade(self, intent):

        leg = intent.get('leg')
        price = intent.get('price')
        outcome = intent.get('outcome')
        side = intent.get('side')
        order_type = intent.get('order_type')
        share = self._cal_trade_size_on_leg(leg, price)
        self._process_order(outcome, order_type, share, price = 0)

        

    def _process_order(self, outcome, order_type, share_size, price):

        stream_key = f"{self.gs.rolling_timestamps.get('current')}_market"

        event = next((e for e in self.gs.events_metadata if e.get('stream_key') == stream_key))

        if event:

            asset_ids = event.get('asset_ids', [])
            if isinstance(asset_ids, str):
                asset_ids = json.loads(asset_ids)
            asset_id_from_outcome = asset_ids[0] if outcome == "Up" else asset_ids[1]

            if order_type == "market_order":

                order_data = {
                    'asset_id' : asset_id_from_outcome,
                    'amount': share_size,
                    'side': 'BUY',
                    'price': 0,
                }

                print(f"ordering market order {order_data}")

                #order_result = self.execution.market_order(order_data)

            if order_type == "limit_order":

                """ MINIMUM SHARE SIZE IS 5 """    

                order_data = {
                    'asset_id': asset_id_from_outcome,
                    'price': price,
                    'size': share_size,
                    'side': 'BUY'
                }

                print(f"ordering limit order {order_data}")

                #order_result = self.execution.limit_order(order_data)

    
        

           
#------------------------------------------------helpers-----------------------------------------------------#
    def _cal_investment_cost(self):
        
        trades = self.pf_states.active_trades
        total_cumulative_cost = 0.0
        count = len(trades)

        if count < 1 : return

        for trade in trades:

            price = float(trade.get('price', 0))
            size = float(trade.get('size', 0))
            bps = float(trade.get('fee_rate_bps', 0))

            principal = price * size
            fees = principal * (bps / 10000)
            leg_cost = principal + fees

            total_cumulative_cost += leg_cost

        return total_cumulative_cost

    
    def _cal_limit_order(self):

        trades = self.pf_states.active_trades
        target_avg = self.pf_states._total_avg_price
        len = len(self.pf_states.active_trades)
        MIN_POLY_SIZE = self.pf_states.min_share_size

        if not trades:
            print("❌ No active trades to base limit order on.")
            

        if len == 1:
            prev_trade = trades[len - 1] 
            p1 = float(prev_trade.get('price', 0))
            s1 = float(prev_trade.get('size', 0))
            bps1 = float(prev_trade.get('fee_rate_bps', 0))

            f1 = 1 + (bps1 / 10000)
            f2 = f1

            p2_raw = ((target_avg * 2) - (p1 * f1)) / f2
            p2 = round(p2_raw, 2)

            p2 = max(0.01, min(0.99, p2))
            s2 = max(s1, MIN_POLY_SIZE)

            print(f"🎯 Calculated Leg 2 Limit: {p2} for {s2} shares (Target Avg: {target_avg})")
            return p2, s2

        if len == 2:
            pass
            


    def _cal_trade_size_on_leg(self, leg, price):
        op_bal = self.pf_states.operational_balance

        if leg == 1 :

            balance_to_buy = op_bal * 0.10
            
            return balance_to_buy
        
        if 1 < leg <= 4:
           pass
           
        #    active_trades = self.pf_states.active_trades
        #    current_market_id = self.pf_states._current_market_id

        #    market_trades = [t for t in active_trades if t.get('market') == current_market_id]

        #    if market_trades:
        #        pass

if __name__ == "__main__":
    async def main():
        # 1. Initialize the REST client
        clob_rest = ClobRest()
        
        # 2. Authenticate (This is required before any L2 calls)
        await clob_rest.authenticate()
        
        portfolio_manager = PortfolioManager(clob_rest)

        pass
        

        
    

    asyncio.run(main())