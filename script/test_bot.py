import asyncio
from api.clob_wss import ClobWss
from services.clob_service import ClobService
from bot.market_manager import MarketManager

# Dummy callback to see the data
async def mock_callback(msg):
    print(f"📩 Data Received: {msg.get('event_type')}")

async def run_test():
    # 1. Setup
    clob_wss = ClobWss()
    clob_service = ClobService()
    # Assuming you pass clob_wss into MarketManager
    # Note: Use a mock for clob_rest if you don't want to authenticate during testing
    # bot = MarketManager(clob_rest=None, clob_wss=clob_wss)
    
    print("--- 🧪 TEST 1: STARTING STREAM ---")
    # Start the stream in a background task
    stream_task = asyncio.create_task(clob_wss.stream_market_data(mock_callback))
    
    await asyncio.sleep(5) # Let it run for 5 seconds

    print("\n--- 🧪 TEST 2: SIMULATING RECONNECT ---")
    # This should trigger the 'reconnect()' logic you wrote
    await clob_service.simulate_clob_failure()
    
    await asyncio.sleep(10) # Wait to see it reconnect and print "Connected" again

    print("\n--- 🧪 TEST 3: GRACEFUL DISCONNECT ---")
    # This should trigger the 'disconnect()' logic and set is_running = False
    await clob_wss.disconnect()
    
    await asyncio.sleep(5)
    print("--- ✅ TEST COMPLETE ---")

if __name__ == "__main__":
    try:
        asyncio.run(run_test())
    except KeyboardInterrupt:
        pass