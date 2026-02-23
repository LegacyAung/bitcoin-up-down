class PortfolioStates:

    def __init__(self):
        self._wallet_balance = 0.0
        self._balance_for_trade = 0.0

        self._market_metadata = [] 
        self._fulfilled_orders = []
        self._unfulfilled_orders = []


        #signals states
        self._is_sufficient_balance = None
        self._is_sufficient_trade_bal = None
        


    @property
    def get_wallet_balance(self):
        if self._wallet_balance is None : return
        return self._wallet_balance

    def set_wallet_balance(self, value):
        if value is None : return
        self._wallet_balance = value

    @property
    def get_balance_for_trade(self):
        if self._balance_for_trade is None : return
        return self._balance_for_trade
    
    def set_balance_for_trade(self, value):
        if value is None : return
        self._balance_for_trade = value
    
    @property
    def is_sufficient_balance(self):
        if self._is_sufficient_balance is None : return
        return self._is_sufficient_balance
    
    def set_is_sufficient_balance(self, value):
        self._is_sufficient_balance = value


    @property
    def is_sufficient_trade_bal(self):
        if self._is_sufficient_trade_bal is None : return
        return self._is_sufficient_trade_bal
    
    def set_is_sufficient_trade_bal(self, value):
        self._is_sufficient_trade_bal = value

portfolio_states = PortfolioStates()