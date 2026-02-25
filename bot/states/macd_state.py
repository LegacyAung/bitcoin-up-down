class MacdState:
    def __init__(self):
        
        self._macd_1s = None
        self._macd_1m = None



    @property
    def macd_1s(self):
        if self._macd_1s is None :return

        return self._macd_1s
    

    def set_macd_1s(self, values:dict):
        self._macd_1s = values

    @property
    def macd_1m(self):
        if self._macd_1m is None :return

        return self._macd_1m
    

    def set_macd_1s(self, values:dict):
        self._macd_1m = values



macd_states = MacdState()