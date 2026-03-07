import json
import asyncio
from api.clob.clob_rest import ClobRest
from api.gamma.gamma_rest import GammaRest

#from states.portfolio_state import portfolio_states
from py_clob_client.client import  OrderArgs, MarketOrderArgs, OrderType
# from py_clob_client.clob_types import OrderArgs, MarketOrderArgs, OrderType

class Execution:
    def __init__(self, clob_rest):
        self.clob_rest = clob_rest
        #self.pf_states = portfolio_states


    def market_order(self, order_data):
        if not self.clob_rest or not order_data : return

        raw_amount = order_data.get('amount')
        clean_amount = round(float(raw_amount), 2)
        
        market_order_args = MarketOrderArgs(
            token_id = order_data.get('asset_id'),
            amount = clean_amount,
            side = order_data.get('side'),
            price = 0,
        )

        signed_order = self.clob_rest.create_market_order(market_order_args)

        return self.clob_rest.post_order(signed_order, OrderType.FOK)    


    async def limit_order(self, order_data):
        if not self.clob_rest or not order_data : return

        order_args = OrderArgs(
            token_id = order_data.get('asset_id'),
            price = float(order_data.get('price')),
            size = float(order_data.get('size')),
            side = order_data.get('side')
        )

        return self.clob_rest.create_and_post_order(order_args)

    

    async def cancel_order(self, order_id):
        if not self.clob_rest or not order_id: return



    async def cancel_all_orders(self):
        pass


    

if __name__ == "__main__":
    async def main():
        ts = "1772900100"
        params = {"active": "true", "closed": "false"}

        # 1. Initialize Clients
        clob_rest = ClobRest()
        await clob_rest.authenticate()
        gamma = GammaRest(params, ts)

        # 2. Fetch Market Data
        data = await gamma.fetch_slug_event()
        if not data or 'markets' not in data:
            print("❌ Failed to fetch market data")
            return

        market = data['markets'][0]
        token_ids = json.loads(market['clobTokenIds'])

        # 3. Prepare Order
        yes_id = token_ids[0]  # "Up"
        no_id = token_ids[1]
        execute = Execution(clob_rest)
        
        order_data = {
            'asset_id': no_id,
            'amount': 1,  # Buying 'Up' at 40c
            'side': "BUY"
        }

        # 4. EXECUTE (Using await)
        print(f"📡 Sending order for Asset: {no_id}...")
        order_detail = execute.market_order(order_data)
        
        print(f"🧾 Order Result: {order_detail}")

    asyncio.run(main())