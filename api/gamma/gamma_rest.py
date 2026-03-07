import asyncio
from config import EVENTS_GAMMA_ENDPOINT
from ..restful_services import RestfulServices


class GammaRest:
    def __init__(self, params, timestamp, timeout=10):
        self.url = f"{EVENTS_GAMMA_ENDPOINT}btc-updown-15m-{timestamp}"
        self.params = params
        self.timeout = timeout

        self.service = RestfulServices(self.url,self.params,self.timeout)
    async def fetch_slug_event(self):
        res = await self.service.get()
        return res

    
if __name__ == "__main__":

    async def main():
        timestamp = "1772894700"
        params = {
            "active": str(True).lower(),
            "closed": str(False).lower()
        }

        gamma_rest = GammaRest(params,timestamp)

        res = await gamma_rest.fetch_slug_event()

        print(res)


    asyncio.run(main())
    

    




