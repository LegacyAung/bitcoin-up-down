import asyncio


from api.clob.clob_rest import ClobRest
from .portfolio import Portfolio
from ..states.portfolio_state import portfolio_states

class PortfolioManager:
    def __init__(self, clob_rest):
        self.clob_rest = clob_rest
        self.risk_per_resolution = 0.55
        self.decimal_adjustment = 1000000

        self.portfolio =  Portfolio(self.clob_rest)
        self.states = portfolio_states

    
    
    async def handle_portfolio(self):
        if not self.clob_rest : return
        await self._cal_balance()
    
    
    
    async def _cal_balance(self):
        if not self.clob_rest :return

        raw_balance_dict = await self.portfolio.get_balance(asset_type="COLLATERAL") 
        raw_balance = raw_balance_dict.get('balance')
        usd = float(raw_balance) / self.decimal_adjustment
        self.states.set_wallet_balance(usd)

    
    async def _check_unfulfilled_orders(self, condition_id):
        pass

    async def _check_fulfilled_orders(self, condition_id):
        pass





if __name__ == "__main__":
    async def main():
        # 1. Initialize the REST client
        clob_rest = ClobRest()
        
        # 2. Authenticate (This is required before any L2 calls)
        await clob_rest.authenticate()
        
        portfolio_manager = PortfolioManager(clob_rest)

        await portfolio_manager._cal_balance()

        
    

    asyncio.run(main())