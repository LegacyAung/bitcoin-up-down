from bot.states.global_state import state
from bot.states.price_change_state import pc_states
from bot.states.macd_state import macd_states


class DecisionMaker:
    def __init__(self):
        self.gs = state
        self.pc_states = pc_states
        self.macd_states = macd_states

        
        self.bull_bear_1m_collector = []

    async def decide(self):

        rc_greater_than_0 = await self._is_res_count_greater_than_0()

        if not rc_greater_than_0: "waiting for next resolution..."

        current_yes_ask_price = self.pc_states.current_yes_ask_price

        current_no_ask_price = self.pc_states.current_no_ask_price

        tradable_prices = {
            "tradle_y_price" : await self._is_price_at_tradable_zone(current_yes_ask_price),
            "tradle_n_price" : await self._is_price_at_tradable_zone(current_no_ask_price)
        }

        await self._decide_15m_countdown(tradable_prices)


    async def _decide_15m_countdown(self, tradable_prices):

        delta_sec = state.delta_sec

        is_y_tradable = tradable_prices.get('tradle_y_price')
        is_n_tradable = tradable_prices.get('tradle_n_price')

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
    

    async def _decide_macd_1s(self):
        pass
        
        

    
    async def _is_price_at_tradable_zone(self, current_price):

        if 0.0 <= current_price <= 0.19:
            print('False')
            return False
        
        if 0.45 <= current_price <= 0.60:
            print('False')
            return False
        
        if 0.81 <= current_price <= 0.99:
            print('False')
            return False
        
        if current_price == 1.0:
            print('False')
            return False
        
        print('True')
        return True
    
    
    async def _is_res_count_greater_than_0 (self):

        res_count = state.res_count

        if not res_count > 0: return False

        return True
    

    