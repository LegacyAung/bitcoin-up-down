import asyncio
from api.clob_api import ClobApi



class ClobFeatures:

    def __init__(self, api:ClobApi):
        self.api = api
        self.clob_ids = self.api.clob_ids

        self.order_book = {
            "YES": {"bids": [], "ask": []},
            "NO": {"bids": [], "ask": []}
        } 
        
        # State storage for your XGBoost features
        self.latest_state = {
            "yes_price": 0.0,
            "no_price": 0.0,
            "obi": 0.0,
            "spread": 0.0
        }
    
    # --- 1. The Router (The Switchboard) ---
    async def _handle_all_msg(self, msg):
        """Routes incoming data to the correct specific method"""
        event_type = msg.get("event_type")

        if event_type == "book":
            await self._handle_order_book(msg)
        elif event_type == "price_change":
            await self._handle_price_change(msg)
        elif event_type == "last_trade_price":
            await self._handle_last_trade(msg)
        elif event_type == "best_bid_ask":
            await self._handle_bba(msg)
        elif event_type == "new_market":
            await self._handle_new_market(msg)
        elif event_type == "market_resolved":
            await self._handle_resolution(msg)
        
        return event_type
    
    # --- 2. Specific Data Handlers ---
    async def _handle_order_book(self,msg):
        """Splits incoming book data into YES and NO storage"""
        asset_id = msg.get("asset_id")
        
        # Identify the side
        side_label = "YES" if asset_id == self.clob_ids[0] else "NO"
        
        # 2. Extract and format the raw bids/asks
        # Data format: [{'price': '0.89', 'size': '500'}, ...]
        self.order_book[side_label]["bids"] = msg.get("bids", [])
        self.order_book[side_label]["asks"] = msg.get("asks", [])

        # Optional: Print a status update
        # print(f"✅ Updated {side_label} Book | Best Bid: {self.order_books[side_label]['bids'][0]['price'] if self.order_books[side_label]['bids'] else 'N/A'}")


    async def _handle_price_change(self,msg):
        print(msg)


    async def _handle_last_trade(self,msg):
        print(msg)

    async def _handle_bba(self,msg):
        print(msg)
    
    async def _handle_new_market(self,msg):
        print(msg)

    async def _handle_resolution(self,msg):
        print(msg)

    async def start_stream_clob(self):
        """Starts the generic market data stream for price changes."""
        await self.api.stream_market_data(self._handle_all_msg)

if __name__ == "__main__":
    # Initialize the API
    clob_api = ClobApi()
    
    # Initialize the feature tracker
    tracker = ClobFeatures(clob_api)
    
    # Run the event loop
    try:
        asyncio.run(tracker.start_stream_clob())
    except KeyboardInterrupt:
        print("\n🛑 Feature streaming stopped.")