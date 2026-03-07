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

        
        self.price_diff = 0
        self.yes_ask_price = None
        self.no_ask_price = None
        self.is_y_tradable = False
        self.is_n_tradable = False
        self.is_emergency = False
        

        
    async def decide(self):

        rc_greater_than_0 = await self._is_res_count_greater_than_0()

        if not rc_greater_than_0: "waiting for next resolution..."
        
        print(f"Decision is starting...")
        self.price_diff = self.gs.price_diff
        self.yes_ask_price = self.pc_states.current_yes_ask_price
        self.no_ask_price = self.pc_states.current_no_ask_price

        print(f"{type(self.yes_ask_price)}")
        print(f"{type(self.no_ask_price)}")

        if self.yes_ask_price is not None and self.no_ask_price is not None:
            self.is_y_tradable = await self._is_price_at_tradable_zone(self.yes_ask_price)
            self.is_n_tradable = await self._is_price_at_tradable_zone(self.no_ask_price)
        else:
            print("⏳ Waiting for CLOB ask prices...")
            return
        
        self.is_emergency = self.gs.delta_sec <= 180
        
        await self._decide_15m_countdown()


    async def _decide_15m_countdown(self):

        delta_sec = self.gs.delta_sec
        current_leg = self.pf_states.current_leg

        if delta_sec >= 780 :
            print('we are at _ 780')

        if 780 > delta_sec >= 180:
            if current_leg < 3:
                print(f"⚡ Core Window | Delta: {delta_sec}s | Processing Leg {current_leg}")
                await self._decide_on_leg()
            else:
                print(f"✅ Core Legs Finished | Current Leg: {current_leg}. Waiting for Emergency Window.")

        if delta_sec <= 180:
            if current_leg == 3:
                print(f"🚨 Emergency Window | Delta: {delta_sec}s | Final Attempt for Leg {current_leg}")
                await self._decide_on_leg()
            else: 
                print(f"⏹️ Resolution too close. Safety stop active for Legs < 3.")


    
    async def _decide_on_leg(self):
        
        current_leg = self.pf_states.current_leg
        active_trades = self.pf_states.active_trades
        prev_leg_outcome = self.pf_states.prev_leg_outcome

        if current_leg < 1: return


        if current_leg > 4 :
            print('wait for next resolution...current resolution is out of buy')

        if current_leg == 1:
            if len(active_trades) > 0 and prev_leg_outcome is not None: return
            await self._decide_on_price_diff()

        if 1 < current_leg <= 3 :
            if len(active_trades) < 1 and prev_leg_outcome is None : return
            await self._decide_on_direction()

        if current_leg == 4:
            if len(active_trades) < 3 and prev_leg_outcome is None: return

    async def _decide_on_price_diff(self):
        if self.macd_states.macd_1m is None or self.macd_states.macd_1s is None: 
            print("wait for macd signals...")
            return
        
        macd_1m = self.macd_states.macd_1m
        hist_1m_slope = macd_1m.get('h_slope')
        hist_1m_momentum = macd_1m.get('h_momentum')
        
        macd_1s = self.macd_states.macd_1s
        hist_10s_momentum = macd_1s.get('momentum_10s')

        price_diff = abs(self.price_diff)

        is_slope_high = await self._is_macd_slope_high(hist_1m_slope)
        is_slope_positive = await self._is_macd_slope_positive(hist_1m_slope)
        is_y_price_higher = await self._is_y_price_higher()

        if price_diff <= 30:
            print("HELLO _1")
            if is_slope_high and is_slope_positive:
                
                await self._decide_bullish_buy()

            if is_slope_high and not is_slope_positive:
                
                await self._decide_bearish_buy()

            if not is_slope_high:
                
                if hist_1m_momentum == "BULLISH":

                    await self._decide_bullish_buy()

                if hist_1m_momentum == "BEARISH":

                    await self._decide_bearish_buy()

                if hist_1m_momentum == "NEUTRAL":
                    
                    if hist_10s_momentum == "STRONG_BULLISH_STAIRCASE":

                        await self._decide_bullish_buy()

                    if hist_10s_momentum == "STRONG_BEARISH_STAIRCASE":

                        await self._decide_bearish_buy()

        
        if 30 < price_diff <= 130:

            print("HELLO _2")
            if hist_1m_momentum == "BULLISH":
                await self._decide_bullish_buy()
            
            if hist_1m_momentum == "BEARISH":
                await self._decide_bearish_buy()

            if hist_1m_momentum == "NEUTRAL":
                
                if hist_10s_momentum == "STRONG_BULLISH_STAIRCASE":

                    await self._decide_bullish_buy()

                if hist_10s_momentum == "STRONG_BEARISH_STAIRCASE":

                    await self._decide_bearish_buy()

        
        if price_diff > 130:
            print("HELLO _3")

            if is_y_price_higher:
                await self._decide_bullish_buy()
            else:
                await self._decide_bearish_buy() 

    async def _decide_on_direction(self):
        pass
    
    async def _decide_bullish_buy(self, order_type):
        is_y_tradable = self.is_y_tradable

        if is_y_tradable:
            if self.pf_states.is_pending: return
            
            self.pf_states.set_pending(status=True)
            
            trade_intent = {
                    'market_id': self.pf_states._current_market_id,
                    'side': 'BUY',
                    'outcome': 'UP',
                    'leg': self.pf_states.current_leg,
                    'status': 'NEW',
                    'order_type': order_type,
                    'price': self.yes_ask_price
            }

            self.pf_states.set_trade_intents(trade_intent)


    async def _decide_bearish_buy(self):
        is_n_tradable = self.is_n_tradable

        if is_n_tradable:
            if self.pf_states.is_pending: return
            
            self.pf_states.set_pending(status=True)
            
            trade_intent = {
                    'market_id': self.pf_states._current_market_id,
                    'side': 'BUY',
                    'outcome': 'Up',
                    'leg': self.pf_states.current_leg,
                    'status': 'NEW',
                    'order_type': 'market_order',
                    "price": self.no_ask_price
            }

            self.pf_states.set_trade_intents(trade_intent)



    
        
        
    
    


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
    
    async def _is_y_price_higher(self):
        if self.yes_ask_price and self.no_ask_price is None : return

        return self.yes_ask_price > self.no_ask_price
        
        