import os
from dotenv import load_dotenv

load_dotenv()

EVENTS_GAMMA_ENDPOINT = os.getenv("GAMMA_EVENTS_ENDPOINT")
CLOB_ENDPOINT = os.getenv("CLOB_ENDPOINT")
RELAYER_ENDPOINT = os.getenv("RELAYER_ENDPOINT")
CLOB_WEBSOCKET = os.getenv("CLOB_WEBSOCKET")
RTDS_WEBSOCKET = os.getenv("RTDS_WEBSOCKET")
BINANCE_WEBSOCKET = os.getenv("BINANCE_WEBSOCKET")
BINANCE_ENDPOINT = os.getenv("BINANCE_ENDPOINT")

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
FUNDER_ADDRESS = os.getenv("FUNDER_ADDRESS")
CHAIN_ID = os.getenv("CHAIN_ID")



BUILDER_CREDENTIALS = {
    "key":os.getenv("BUILDER_API_KEY"),
    "secret":os.getenv("BUILDER_SECRET"),
    "passphrase":os.getenv("BUILDER_PASSPHRASE")
}

if not EVENTS_GAMMA_ENDPOINT:
    EVENTS_GAMMA_ENDPOINT = "https://gamma-api.polymarket.com/events/slug/"


if not CLOB_ENDPOINT:
    CLOB_ENDPOINT = "https://clob.polymarket.com"


if not CLOB_WEBSOCKET:
    CLOB_WEBSOCKET = "wss://ws-subscriptions-clob.polymarket.com"


if not RTDS_WEBSOCKET:
    RTDS_WEBSOCKET = "wss://ws-live-data.polymarket.com"