from bot.global_state import state

class BotTest:
    def __init__(self, wallet_balance,):
        
        self.target_total = 0.8
        self.current_positions = {
            'yes': {'avg_price': 0.0, 'size': 0},
            'no':{'avg_price': 0.0, 'size': 0}
        }

        self.wallet_balance = wallet_balance

    async def decide_buy(self, price, size):
        pass

    


if __name__ == "__main__":
    pass
