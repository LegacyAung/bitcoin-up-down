class PortfolioStates:

    def __init__(self):
        # Bankroll Configuration
        self._wallet_balance = 0.0
        self._operational_balance = 200.0
        
        self._max_legs = 4
        self._current_leg = 1
        self._prev_leg_outcome = None   # Tracks "Up" or "Down"
        self._is_pending = False
        self._current_market_id = None

        # This represents confirmed trades (Positions)
        self._active_trades = []
        self._open_orders = []


    @property
    def is_pending(self):
        return self._is_pending
    
    def set_pending(self, status:bool):
        if status is None : return
        self._is_pending = status


    @property
    def current_leg(self):
        return self._current_leg
    
    def increment_leg(self):
        if self._current_leg <= self._max_legs:
            self._current_leg += 1

    @property
    def prev_leg_outcome(self):
        return self._prev_leg_outcome
    
    def set_prev_leg_outcome(self, outcome):
        if outcome is None : return
        self._prev_leg_outcome = outcome

    @property
    def max_legs(self):
        return self._max_legs
    
    def set_max_legs(self, value:int):
        if value is None: return
        self._max_legs = value

    @property
    def wallet_balance(self):
        return self._wallet_balance

    def set_wallet_balance(self, value:float):
        if value is None: return
        self._wallet_balance = value

    @property
    def active_trades(self):
        return self._active_trades
    
    def set_active_trades(self, value):
        if value is None: return
        self._active_trades.append(value)


    @property
    def open_orders(self):
        return self._open_orders
    
    def set_open_orders(self, value):
        if value is None: return
        self._open_orders.append(value)
        
        




portfolio_states = PortfolioStates()