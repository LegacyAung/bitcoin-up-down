import httpx


class RestfulServices:
    def __init__(self, url, payloads, timeout=10):
        """
        Universal Restful Service
        :param url: The rest endpoint.
        :param payload: The subscription JSON.
        """
        self.url = url
        self.params = payloads
        self.timeout = timeout

        self.http_client = httpx.AsyncClient()

    async def get(self):
        try: 
            res= await self.http_client.get(url= self.url,params=self.params,timeout=self.timeout)
            res.raise_for_status()
            return res.json() 

        except httpx.RequestError as e:
            print(f"❌ Binance API Error: {e}")
            return None