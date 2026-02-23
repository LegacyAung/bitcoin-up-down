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

        self._is_greater_than_50 = None
        self._is_less_than_50 = None
        self._is_bw_50_85 = None
        self._is_bw_20_50 = None
        self._is_less_than_20 = None
        self._is_greater_than_85 = None


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



# --- Boolean Signals --- # 
    @property
    def is_greater_than_50(self):
        return self._is_greater_than_50

    
    def set_is_greater_than_50(self, value):
        if value is None: self._is_greater_than_50 = None

        if value >= 50:
            self._is_greater_than_50 = True
        else:
            self._is_greater_than_50 = False


    @property
    def is_less_than_50(self):
        return self._is_less_than_50

    
    def set_is_less_than_50(self, value):
        if value is None: self._is_less_than_50 = None

        if value < 50:
            self._is_less_than_50 = True
        else:
            self._is_less_than_50 = False

    @property
    def is_bw_50_85(self):
        return self._is_bw_50_85

    
    def set_is_bw_50_85(self, value):
        if value is None: self._is_bw_50_85 = None

        if 50 < value <= 85:
            self._is_bw_50_85 = True
        else:
            self._is_bw_50_85 = False

    @property
    def is_bw_20_50(self):
        return self._is_bw_20_50

    
    def set_is_bw_20_50(self, value):
        if value is None: self._is_bw_20_50 = None

        if 20 < value <= 50:
            self._is_bw_20_50 = True
        else:
            self._is_bw_20_50 = False


    @property
    def is_less_than_20(self):
        return self._is_less_than_20()

    
    def set_is_less_than_20(self, value):
        if value is None: self._is_less_than_20 = None

        if value <= 20:
            self._is_less_than_20 = True
        else:
            self._is_less_than_20 = False
    

    @property
    def is_greater_than_85(self):
        return self._is_greater_than_85()

    
    def set_is_greater_than_85(self, value):
        if value is None: self._is_greater_than_85 = None

        if value >= 85:
            self._is_greater_than_85 = True
        else:
            self._is_greater_than_85 = False

pc_state = PriceChangeState()