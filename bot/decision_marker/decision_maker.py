from states.global_state import state


class DecisionMaker:
    def __init__(self):
        self.gs = state

        

    async def decide_on_res_count(self):

        res_count = state.res_count

        if not res_count > 0: return False

        return True

    async def decide_on_15m_countdown(self):

        delta_sec = state.delta_sec

        if delta_sec >= 780 :
            pass # "Time before 13 mins, this is to do nothing at all here but wait to watch the trend...Here just study the momentum of macd 1m"
        elif 780 > delta_sec >= 660:  
            pass # "[If] momentum is strong which i mean is macd hist(1m) is high and the weighted 1s is also following up with the moment (buy the trend) follow the trend [else] buy the price with good odds"
        elif 660 > delta_sec >= 540:
            pass # "[If] "
        elif 540 > delta_sec >= 420:
            pass
        elif 420 > delta_sec >= 300:
            pass
        elif 300 > delta_sec >= 180:
            pass
        elif 180 > delta_sec >= 70:
            pass
        else:
            pass

    
    async def is_price_at_tradable_zone(self, current_price):

        if 0.0 <= current_price <= 0.19:
            return False
        
        if 0.45 <= current_price <= 0.60:
            return False
        
        if 0.81 <= current_price <= 0.99:
            return False
        
        if current_price == 1.0:
            return False
        
        return True
    

    