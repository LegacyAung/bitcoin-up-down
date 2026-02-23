from states.portfolio_state import portfolio_states

class PortfolioSignal:
    def __init__(self):

        self.ps = portfolio_states


    async def is_sufficient_balance(self):
        if self.ps.get_wallet_balance <= 40:
            self.ps.set_is_sufficient_balance(False)
        else: 
            self.ps.set_is_sufficient_balance(True)

    
    async def is_sufficient_trade_bal(self):
        if self.ps.get_balance_for_trade <= 20:
            self.ps.set_is_sufficient_trade_bal(False)
        else:
            self.ps.set_is_sufficient_trade_bal(True)

    