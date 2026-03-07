import asyncio
from api.clob.clob_rest import ClobRest
from .portfolio import Portfolio
from executor import Execution
from ..states.portfolio_state import portfolio_states
from ..states.global_state import state



class PortfolioManager:

    def __init__(self, clob_rest):

        self.clob_rest = clob_rest
        self.portfolio =  Portfolio(self.clob_rest)
        self.execution = Execution(self.clob_rest)

        self.gs = state
        self.pf_states = portfolio_states

    
    async def call_portfolio(self):
        await self._portfolio_caller()


    async def _portfolio_caller(self):
        """Calling all the methods from portfolio file update the wallet states"""
        if not self.clob_rest : return

        current_slug_ts = self.gs.rolling_timestamps.get('current')

        events_meta = self.gs.events_metadata

        if len(events_meta) <= 0 : return

        """Calling get_balance"""

        raw_balance_dict = await self.portfolio.get_balance(asset_type="COLLATERAL") 
        raw_balance = raw_balance_dict.get('balance')
        total_bankroll = float(raw_balance)/ 1000000

        self.pf_states.set_wallet_balance(total_bankroll)

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

                self.pf_states.set_open_orders(open_orders)
                self.pf_states.set_active_trades(active_trades)
                
                
    async def _trade_intents_handler(self):

        """Handling trade approval states that is passed down from decision maker"""
        
        intent = await self.pf_states.trade_queue.get()

        print(f"got the trade intent from decision maker {intent}")

        await self._process_trade(intent)
        
        self.pf_states.trade_queue.task_done()


    async def _process_trade(self, intent):

        stream_key = f"{self.gs.rolling_timestamps.get('current')}_market"

        leg = intent.get('leg')
        price = intent.get('price')
        outcome = intent.get('outcome').upper()
        side = intent.get('side')
        order_type = intent.get('order_type')
        
        share = self._cal_trade_size_on_leg(leg, price)

        event = next((e for e in self.gs.events_metadata if e.get('stream_key') == stream_key))

        if event:

            asset_ids = event.get('asset_ids', [])
            asset_id_from_outcome = asset_ids[0] if outcome == "UP" else asset_ids[1]

            if order_type == "market_order":

                order_date = {
                    'asset_id' : asset_id_from_outcome,
                    'amount': share,
                    'side': side,
                    'price': 0,
                }

                print(f"ordering market order {order_data}")

                #order_result = self.execution.market_order(order_data)

            if order_type == "limit_order":
                """ MINIMUM SHARE SIZE IS 5 """    

                order_data = {
                    'asset_id': asset_id_from_outcome,
                    'price': price,
                    'size': share,
                    'side': side
                }

                print(f"ordering market order {order_data}")
                
                #order_result = self.execution.limit_order(order_data)

            

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

    def _cal_profit(self,):
        pass
        

           
#------------------------------------------------helpers-----------------------------------------------------#

    def _generate_random_float(self):
        pass

if __name__ == "__main__":
    async def main():
        # 1. Initialize the REST client
        clob_rest = ClobRest()
        
        # 2. Authenticate (This is required before any L2 calls)
        await clob_rest.authenticate()
        
        portfolio_manager = PortfolioManager(clob_rest)

        pass
        

        
    

    asyncio.run(main())