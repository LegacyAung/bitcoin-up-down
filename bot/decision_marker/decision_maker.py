import asyncio
from bot.states.global_state import state
from bot.states.price_change_state import pc_states
from bot.states.macd_state import macd_states
from bot.states.portfolio_state import portfolio_states

class DecisionMaker:
    def __init__(self):
        self.gs = state
        self.pc_states = pc_states
        self.macd_states = macd_states
        self.pf_states = portfolio_states

        
        self.bull_bear_1m_weight_collector = []
        self.legs_countdown = 4

        


    async def decide(self):

        rc_greater_than_0 = await self._is_res_count_greater_than_0()

        if not rc_greater_than_0: "waiting for next resolution..."
        
        print(f"Decision is starting...")
        current_price_diff = self.gs.price_diff
        current_yes_ask = self.pc_states.current_yes_ask_price
        current_no_ask = self.pc_states.current_no_ask_price

        if current_yes_ask is None or current_no_ask is None: 
            print("⏳ Waiting for CLOB price data...")
            return
        
        tradable_prices = {
            "tradable_y_price" : await self._is_price_at_tradable_zone(current_yes_ask),
            "tradable_n_price" : await self._is_price_at_tradable_zone(current_no_ask)
        }

        ask_prices = {
            'current_y' : current_yes_ask,
            'current_n' : current_no_ask
        }

        decision_data  = {
            'tradable_prices': tradable_prices,
            'ask_prices': ask_prices,
            'current_price_diff': current_price_diff
        }

        await self._decide_15m_countdown(decision_data)


    async def _decide_15m_countdown(self, decision_data):

        delta_sec = state.delta_sec

        if delta_sec >= 780 :
            print('we are at _ 780')


        if 780 > delta_sec >= 180:
            print('we are at _ (780 - 180)')
            await asyncio.gather(
                self._decide_bullish_buy(decision_data),
                self._decide_bearish_buy(decision_data)
            )
            await self._decide_bullish_buy(decision_data)

        if delta_sec <= 180:
            print('we are at _ 180')


    async def _decide_bullish_buy(self, decision_data):
        if self.macd_states.macd_1m is None or self.macd_states.macd_1s is None: 
            print("wait for macd signals...")
            return
        
        print("🟢deciding for bullish buy....🟢")
        
        macd_1m = self.macd_states.macd_1m
        hist_1m_slope = macd_1m.get('h_slope')
        hist_1m_momentum = macd_1m.get('h_momentum')
        hist_1m_squeeze = macd_1m.get('h_squeeze')

        price_diff = abs(decision_data.get("current_price_diff"))
        tradable_prices = decision_data.get("tradable_prices")
        is_tradable_price = tradable_prices.get("tradable_y_price")

        ask_prices = decision_data.get('ask_prices')
        yes_ask_price = ask_prices.get('current_y')

        is_slope_high = await self._is_macd_slope_high(hist_1m_slope)
        is_slope_positive = await self._is_macd_slope_positive(hist_1m_slope)



        if price_diff <= 30:
            
            if is_slope_high and is_slope_positive and is_tradable_price:
                # Here we call 
                print(f"💰BUY YES PRICE AT {yes_ask_price} FOR SHARE SIZE 10💰")

            if not is_slope_high and is_slope_positive and is_tradable_price:
                print(f"YES PRICE : {yes_ask_price}")
                print(f"💰BUY YES PRICE B/W LIMIT ORDER BETWEEN 0.2 & 0.4💰")
        
        
        if 30 < price_diff <= 130:
            print('hello_2')
            


        if price_diff > 130:
            print('hello_3')


    async def _decide_bearish_buy(self, decision_data):
        if self.macd_states.macd_1m is None or self.macd_states.macd_1s is None: 
            print("wait for macd signals...")
            return
        
        print("🔴deciding for bearish buy....🔴")
        
        macd_1m = self.macd_states.macd_1m
        hist_1m_slope = macd_1m.get('h_slope')

        price_diff = abs(decision_data.get("current_price_diff"))
        tradable_prices = decision_data.get("tradable_prices")
        is_tradable_price = tradable_prices.get("tradable_n_price")

        ask_prices = decision_data.get('ask_prices')
        no_ask_price = ask_prices.get('current_n')


        if price_diff <= 30:

            is_slope_high = await self._is_macd_slope_high(hist_1m_slope)
            is_slope_positive = await self._is_macd_slope_positive(hist_1m_slope)

            if is_slope_high and not is_slope_positive and is_tradable_price:
                print(f"💰BUY NO PRICE AT {no_ask_price} FOR SHARE SIZE 10💰")

            if not is_slope_high and not is_slope_positive and is_tradable_price:
                print(f"NO PRICE : {no_ask_price}")
                print(f"💰BUY NO PRICE B/W LIMIT ORDER BETWEEN 0.2 & 0.4💰")
        
        
        if 30 < price_diff <= 130:
            print('hello_2') 


        if price_diff > 130:
            print('hello_3')
        
    


#----------------------------------HELPERS----------------------------------#  

        
    async def _is_price_at_tradable_zone(self, current_price):

        if 0.0 <= current_price <= 0.19:
            print('False')
            return False
        
        if 0.50 <= current_price <= 0.60:
            print('False')
            return False
        
        if 0.81 <= current_price <= 1.0:
            print('False')
            return False
        
        print('True')
        return True
    
    
    async def _is_res_count_greater_than_0 (self):

        res_count = state.res_count

        if not res_count > 0: return False

        return True
    
    async def _is_macd_slope_high(self, h_slope):

        if h_slope is None : return

        return abs(h_slope) > 2.0

    async def _is_macd_slope_positive(self, h_slope):

        if h_slope is None : return

        return h_slope > 0