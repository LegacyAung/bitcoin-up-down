import asyncio

class PortfolioStates:

    def __init__(self):
        # Bankroll Configuration
        self._wallet_balance = 1000.0
        self._operational_balance = 200.0
        self._total_avg_price = 0.85
        self._min_share_size = 5.0
        
        self._max_legs = 4
        self._current_leg = 1
        self._prev_leg_outcome = None   # Tracks "Up" or "Down"
        self._is_pending = False
        self._current_market_id = None

        # This represents confirmed trades (Positions) this can only be updated after execution
        self._active_trades = []
        self._update_active_trade_event = asyncio.Event()

        self._open_orders = []
        
        # This is pending states from decision maker
        self._trade_queue = asyncio.Queue()

    
    @property
    def total_avg_price(self):
        return self._total_avg_price
    

    @property
    def min_share_size(self):
        return self._min_share_size


    @property
    def wallet_balance(self):
        return self._wallet_balance

    def set_wallet_balance(self, value:float):
        if value is None : return
        self._wallet_balance = value

    @property
    def operational_balance(self):
        return self._operational_balance

    def set_operational_balance(self, value:float):
        if value is None : return
        self._operational_balance = float(value)
    
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
    
    def set_active_trades(self, data):
        has_changed = False

        if isinstance(data, dict) and 'id' in data:
            if not any(t.get('id') == data['id'] for t in self._active_trades):
                self._active_trades.append(data)
                has_changed = True
        elif isinstance(data, list):
            self._active_trades = [t for t in data if isinstance(t, dict) and t]
            has_changed = True

        if has_changed:
            self._update_active_trade_event.set()
            self._update_active_trade_event.clear()

    @property
    def open_orders(self):
        return self._open_orders
    
    def set_open_orders(self, data):
        if isinstance(data, dict) and 'id' in data:
            if not any(o.get('id') == data['id'] for o in self.open_orders):
                self._open_orders.append(data)
        
        elif isinstance(data, list):
            self._open_orders = [o for o in data if isinstance(o, dict) and o]


    @property
    def trade_queue(self):
        return self._trade_queue


    def set_trade_intents(self, value):
        if value is None: return

        if 'status' not in value:
            value['status'] = 'NEW'

        self._trade_queue.put_nowait(value)

    
    def reset_for_new_resolution(self, market_id):
        if market_id is None : return

        if self._current_market_id != market_id:
            print(f"🔄 New Resolution Detected: {market_id}. Resetting Leg Counter.")
            self._current_market_id = market_id
            self._current_leg = 1 
            self._prev_leg_outcome = None
            self._is_pending = False
            self._active_trades = []
            self._open_orders = []
        
        




portfolio_states = PortfolioStates()