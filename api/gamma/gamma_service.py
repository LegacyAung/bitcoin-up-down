import requests


# Get Request to GAMMA endpoint
def get_gamma_rest(url, params, timeout):
    try: 
        res = requests.get(url, params=params, timeout=timeout)
        res.raise_for_status()
        return res.json() 

    except requests.exceptions.RequestException as e:
        print(f"❌ Gamma API Error: {e}")
        return None