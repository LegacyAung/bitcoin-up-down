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

        self.current_yes_ask = 0.0
        self.current_no_ask = 0.0


    async def decide(self):

        rc_greater_than_0 = await self._is_res_count_greater_than_0()

        if not rc_greater_than_0: "waiting for next resolution..."
        
        print(f"Decision is starting...")

        current_yes_ask = self.pc_states.current_yes_ask_price
        current_no_ask = self.pc_states.current_no_ask_price

        if current_yes_ask is None or current_no_ask is None: 
            print("⏳ Waiting for CLOB price data...")
            return
        
        self.current_yes_ask = current_yes_ask
        self.current_no_ask = current_no_ask
        
        print(current_yes_ask)
        print(current_no_ask)

        tradable_prices = {
            "tradable_y_price" : await self._is_price_at_tradable_zone(current_yes_ask),
            "tradable_n_price" : await self._is_price_at_tradable_zone(current_no_ask)
        }

        ask_prices = {
            'current_y' : current_yes_ask,
            'current_n' : current_no_ask
        }

        await self._decide_15m_countdown(tradable_prices, ask_prices)


    async def _decide_15m_countdown(self, tradable_prices):

        delta_sec = state.delta_sec

        if delta_sec >= 780 :
            print('we are at _ 780')
            

        elif 780 > delta_sec >= 660:
            print('we are at _ 660')
            await asyncio.gather(
                self._decide_bullish_buy(tradable_prices),
                self._decide_bearish_buy(tradable_prices)
            )
        elif 660 > delta_sec >= 540:
            print('we are at _ 540')
            await asyncio.gather(
                self._decide_bullish_buy(tradable_prices),
                self._decide_bearish_buy(tradable_prices)
            )
        elif 540 > delta_sec >= 420:
            print('we are at _ 420')
            await asyncio.gather(
                self._decide_bullish_buy(tradable_prices),
                self._decide_bearish_buy(tradable_prices)
            )
        elif 420 > delta_sec >= 300:
            print('we are at _ 300')
            await asyncio.gather(
                self._decide_bullish_buy(tradable_prices),
                self._decide_bearish_buy(tradable_prices)
            )
        elif 300 > delta_sec >= 180:
            print('we are at _ 180')
            await asyncio.gather(
                self._decide_bullish_buy(tradable_prices),
                self._decide_bearish_buy(tradable_prices)
            )
        elif 180 > delta_sec >= 70:
            print('we are at _ 180')
            
    
    async def _decide_bullish_buy(self, tradable_prices):

        if self.macd_states.macd_1m is None or self.macd_states.macd_1s is None:
            return

        print("deciding for bullish buy....")
    
        macd_1m = self.macd_states.macd_1m
        hist_momentum_1m = macd_1m['h_momentum']
        hist_side = macd_1m['h_side']
        hist_squeeze = macd_1m['h_squeeze']


        macd_1s = self.macd_states.macd_1s
        net_bias = macd_1s['net_bias']

        if not tradable_prices['tradable_y_price']: return

        if self.legs_countdown <= 1 : return

        if hist_squeeze == "SQUEEZE_ACTIVE" :
            print(net_bias)

        if self.gs.price_diff > 120 and hist_momentum_1m == "BULLISH" and hist_side == "OVERALL_BULLSIDE" :
            print(f"Buy YES price at {self.prices['current_yes_ask']} for ${6.66}")

        if hist_momentum_1m == "BULLISH" and hist_side == "OVERALL_BULLSIDE" :
            print(f"Buy YES price at {self.prices['current_yes_ask']} for ${6.66}")


    async def _decide_bearish_buy(self, tradable_prices):

        if self.macd_states.macd_1m is None or self.macd_states.macd_1s is None:
            return
        
        print("deciding for bullish buy....")

        macd_1m = self.macd_states.macd_1m
        hist_momentum_1m = macd_1m['h_momentum']

        if self.gs.price_diff < -120 and hist_momentum_1m == "BEARISH" and tradable_prices['tradle_n_price']  and self.legs_countdown > 0:

            print(f"Buy NO price at {self.prices['current_no_ask']} for ${6.66}") 

        

    
    async def _is_price_at_tradable_zone(self, current_price):

        if 0.0 <= current_price <= 0.19:
            print('False')
            return False
        
        if 0.45 <= current_price <= 0.60:
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
    

    