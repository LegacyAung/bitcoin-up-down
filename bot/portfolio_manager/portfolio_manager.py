import asyncio

from api.clob.clob_rest import ClobRest
from py_clob_client.client import BalanceAllowanceParams, TradeParams, OpenOrderParams 

class PortfolioManager:
    def __init__(self, clob_rest):
        
        self.clob_rest = clob_rest

        self.active_legs = []


    async def get_balance(self, asset_type, token_id=None):
        if not self.clob_rest : return

        params = BalanceAllowanceParams(
            asset_type=asset_type.upper(),
            token_id=token_id
        )

        try:
            balance_data = self.clob_rest.get_balance_allowance(params)
            return balance_data
        except Exception as e:
            print(f"❌ Error fetching balance: {e}")
            return None
        
    async def get_active_positions(self,maker_address,market, asset_id): # maker_address == funder_address , market == condition_id 
        if not self.clob_rest : return
        
        params = TradeParams(
            id=None,
            maker_address=maker_address,
            market=market,
            asset_id=asset_id,
            before = None,
            after= None
        )

        try:
            return self.clob_rest.get_trades(params)
        except Exception as e:
            print(f"❌ Error fetching active positions: {e}")
            return None
        
    async def get_order_position(self, order_id):
        if not self.clob_rest : return

        try: 
            return self.clob_rest.get_Order(order_id)
        except Exception as e:
            print(f"❌ Error fetching active positions: {e}")
            return None
        
    async def get_order_positions(self, order_id = None, condition_id = None, asset_id = None):
        if not self.clob_rest : return

        params = OpenOrderParams(
            id = order_id,
            market = condition_id,
            asset_id = asset_id
        )
        try:
            return self.clob_rest.get_open_orders(params)
        except Exception as e:
            print(f"❌ Error fetching order positions: {e}")
            return None
    
    


if __name__ == "__main__":
    
    async def main():
        # 1. Initialize the REST client
        clob_rest = ClobRest()
        
        # 2. Authenticate (This is required before any L2 calls)
        await clob_rest.authenticate()
        
        # 3. Initialize the Portfolio Manager
        portfolio = PortfolioManager(clob_rest)

        # 4. Check USDC Balance (Collateral)
        print("\n--- Checking USDC Balance ---")
        balance = await portfolio.get_balance(asset_type="COLLATERAL")
        
        return balance 

    # This is the standard way to launch an async main in Python 3.7+
    asyncio.run(main())
