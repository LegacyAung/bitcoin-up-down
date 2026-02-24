class PriceChangeState:
    def __init__(self):
        self._current_yes_ask_price = 0.0
        self._current_no_ask_price = 0.0
        self._current_yes_bid_price = 0.0
        self._current_no_bid_price = 0.0

        self._next_yes_ask_price = 0.0
        self._next_no_ask_price = 0.0
        self._next_yes_bid_price = 0.0
        self._next_no_bid_price = 0.0

     


# --- Numerical Signals --- #    

    @property
    def current_yes_ask_price(self):
        return self._current_yes_ask_price
    
    def set_current_yes_ask_price(self, value):
        if value is None: self._current_yes_ask_price = 0.0
        
        self._current_yes_ask_price = value

    @property
    def current_no_ask_price(self):
        return self._current_no_ask_price
    
    
    def set_current_no_ask_price(self, value):
        if value is None: self._current_no_ask_price = 0.0

        self._current_no_ask_price = value

    @property
    def current_yes_bid_price(self):
        return self._current_yes_bid_price
    
    
    def set_current_yes_bid_price(self, value):
        if value is None: self._current_yes_bid_price = 0.0

        self._current_yes_bid_price = value
    
    @property
    def current_no_bid_price(self):
        return self._current_no_bid_price
    
    
    def set_current_no_bid_price(self, value):
        if value is None: self._current_no_bid_price = 0.0

        self._current_no_bid_price = value

    
    
    @property
    def next_yes_ask_price(self):
        return self._next_yes_ask_price
    
    
    def set_next_yes_ask_price(self, value):
        if value is None: self._next_yes_ask_price = 0.0

        self._next_yes_ask_price = value

    @property
    def next_no_ask_price(self):
        return self._next_no_ask_price
    
    
    def set_next_no_ask_price(self, value):
        if value is None: self._next_no_ask_price = 0.0

        self._next_no_ask_price = value
    
    @property
    def next_yes_bid_price(self):
        return self._next_yes_bid_price
    
    
    def set_next_yes_bid_price(self, value):
        if value is None: self._next_yes_bid_price = 0.0

        self._next_yes_bid_price = value

    @property
    def next_no_bid_price(self):
        return self._next_no_bid_price
    
    
    def set_next_no_bid_price(self, value):
        if value is None: self._next_no_bid_price = 0.0
        
        self._next_no_bid_price = value





pc_states = PriceChangeState()