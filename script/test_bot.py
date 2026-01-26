import asyncio
import json
from api.clob.clob_wss import ClobWss
from api.gamma.gamma_rest import fetch_current_event_slug


class OrderbookManager:
    def __init__(self, clob_tokenids):
        # Polymarket typically returns [YES_ID, NO_ID]
        self.yes_id = clob_tokenids[0]
        self.no_id = clob_tokenids[1]

        self.assets = {
            self.yes_id: {"side": "YES", "bids": {}, "asks": {}},
            self.no_id: {"side": "NO", "bids": {}, "asks": {}},
        }

    def update(self, msg):
        asset_id = msg.get("asset_id")
        if asset_id not in self.assets:
            return

        # Update Bids/Asks with dictionary comprehension for O(1) lookups
        if "bids" in msg:
            self.assets[asset_id]["bids"] = {item["price"]: float(item["size"]) for item in msg["bids"]}
        if "asks" in msg:
            self.assets[asset_id]["asks"] = {item["price"]: float(item["size"]) for item in msg["asks"]}

    def get_best_prices(self, asset_id):
        bids = self.assets[asset_id]["bids"]
        asks = self.assets[asset_id]["asks"]

        # best_bid = Highest price someone wants to buy at
        best_bid = max(bids.keys(), key=float) if bids else None
        # best_ask = Lowest price someone wants to sell at
        best_ask = min(asks.keys(), key=float) if asks else None

        return best_bid, best_ask

    def get_pair_cost(self):
        """Calculates the cost to buy 1 YES and 1 NO share at current market prices."""
        _, yes_ask = self.get_best_prices(self.yes_id)
        _, no_ask = self.get_best_prices(self.no_id)

        if yes_ask and no_ask:
            return float(yes_ask) + float(no_ask)
        return None
    



class TestBot:
    def __init__(self, clob_wss, clob_ids):
        self.clob_wss = clob_wss
        self.ob_manager = OrderbookManager(clob_ids)
        self.budget = 50.0  # Your limit

    async def start_clob_wss(self):
        print("🚀 Starting WebSocket Stream...")
        await self.clob_wss.stream_market_data(self.clob_callback_data)

    async def clob_callback_data(self, msg):
        if msg.get('event_type') == 'book':
            print(msg)
            # self.ob_manager.update(msg)
            
            # # 1. Get IDs
            # y_id, n_id = self.ob_manager.yes_id, self.ob_manager.no_id
            
            # # 2. Calculate Taker Cost (What you have now)
            # taker_cost = self.ob_manager.get_pair_cost()
            
            # # 3. Calculate Maker Cost (The price if you place a Limit Order)
            # y_bid, _ = self.ob_manager.get_best_prices(y_id)
            # n_bid, _ = self.ob_manager.get_best_prices(n_id)
            
            # if y_bid and n_bid:
            #     maker_cost = float(y_bid) + float(n_bid)
                
            #     # 4. Calculate Imbalance (OBI) for YES
            #     y_bids_vol = sum(self.ob_manager.assets[y_id]['bids'].values())
            #     y_asks_vol = sum(self.ob_manager.assets[y_id]['asks'].values())
            #     y_obi = (y_bids_vol - y_asks_vol) / (y_bids_vol + y_asks_vol) if (y_bids_vol + y_asks_vol) > 0 else 0

            #     # Print a clean dashboard
            #     print(f"--- Market Pulse ---")
            #     print(f"Taker: ${taker_cost:.3f} | Maker: ${maker_cost:.3f}")
            #     print(f"YES Imbalance: {y_obi:+.2f} {'📈' if y_obi > 0.2 else '📉' if y_obi < -0.2 else '⚖️'}")
                
            #     if taker_cost < 0.95:
            #         print("🔥 LEG 1 TRIGGER: TAKER OPPORTUNITY!")
            #     elif maker_cost < 0.95:
            #         print("🎯 STRATEGY: Place Limit Orders to capture $0.95 pair.")

    async def execute_strategy_logic(self, current_cost):
        # Placeholder for your buying logic
        # Here is where you'd check which leg you are in
        pass

async def main():
    # 1. Fetch Market Metadata
    try:
        current_event = fetch_current_event_slug()
        
        current_market = current_event['markets'][0]
        
        # Parse the IDs (string to list)
        clob_ids = json.loads(current_market['clobTokenIds'])
        print(f"📊 Market Found: {current_event.get('title')}")
        print(f"🆔 YES ID: {clob_ids[0]}\n🆔 NO ID: {clob_ids[1]}")

        # 2. Initialize Bot and WSS
        clob_wss = ClobWss()
        test_bot = TestBot(clob_wss=clob_wss, clob_ids=clob_ids)

        # 3. Run
        await test_bot.start_clob_wss()
        
    except Exception as e:
        print(f"⚠️ Initialization Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())