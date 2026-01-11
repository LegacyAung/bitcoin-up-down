from utils.binance_dataframe_util import format_binance_data, save_to_csv
from api.binance_client_rest import get_binance_history



def fetch_process_binance_history(symbol="BTCUSDT"):
    binance_history = get_binance_history()
    binance_data = format_binance_data(binance_history)
    saved_path = save_to_csv(binance_data, symbol, folder="data")

    return saved_path


if __name__ == "__main__":
    fetch_process_binance_history(symbol="BTCUSDT")


