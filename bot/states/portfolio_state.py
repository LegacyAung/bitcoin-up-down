class PortfolioStates:

    def __init__(self):
        # Current liquid cash in the wallet (USDC)
        self._wallet_balance = 0.0

        # Cash reserved for trades that are LIVE but not yet filled
        self._balance_in_orders = 0.0

        # This represents confirmed trades (Positions)
        self._active_trades = []
        self._open_orders = []
        




portfolio_states = PortfolioStates()