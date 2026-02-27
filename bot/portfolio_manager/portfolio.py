import asyncio
from py_clob_client.client import BalanceAllowanceParams, TradeParams, OpenOrderParams 


class Portfolio:
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
        

    async def get_active_positions(self, trade_params=None): 
        # maker_address == funder_address , market == condition_id  , asset_id == clobTokenId
        if not self.clob_rest : return
        
        params = TradeParams(
            id=trade_params.get('order_id'),
            maker_address=trade_params.get('maker_address'),
            market=trade_params.get('market_id'),
            asset_id=trade_params.get('asset_id'),
            before = None,
            after= None
        )

        try:
            return self.clob_rest.get_trades(params)
        except Exception as e:
            print(f"❌ Error fetching active positions: {e}")
            return None
        
    
    async def get_order_positions(self, order_params=None):
        if not self.clob_rest : return

        params = OpenOrderParams(
            id = order_params.get('order_id'),
            market = order_params.get('market_id'),
            asset_id = order_params.get('asset_id')
        )
        try:
            return self.clob_rest.get_orders(params)
        except Exception as e:
            print(f"❌ Error fetching order positions: {e}")
            return None
        
    


if __name__ == "__main__":
    pass
