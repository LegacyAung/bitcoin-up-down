import requests

def get_binance_rest(url, params, timeout):
    try: 
        res = requests.get(url, params=params, timeout=timeout)
        res.raise_for_status()
        return res.json() 

    except requests.exceptions.RequestException as e:
        print(f"❌ Binance API Error: {e}")
        return None