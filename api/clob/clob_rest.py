import asyncio
import json


from config import CLOB_ENDPOINT, CHAIN_ID, PRIVATE_KEY, FUNDER_ADDRESS
from py_clob_client.client import ClobClient
from py_clob_client.client import ApiCreds
from py_clob_client.clob_types import BalanceAllowanceParams, AssetType
from services.clob_service import ClobService 
from ..gamma.gamma_rest import fetch_current_event_slug


class ClobRest:
    
    def __init__(self):
        self.clob_services = ClobService()
        self.chain_id = CHAIN_ID or 137
        self.private_key = PRIVATE_KEY
        self.funder_address = FUNDER_ADDRESS
        self.clob_endpoint = CLOB_ENDPOINT
        
        self._current_event = self._get_current_event_slug()
        self.current_market = self._current_event['markets'][0]
        self.clob_ids = json.loads(self.current_market['clobTokenIds'])
        self.condition_id = self.current_market['conditionId']

        self.signer_client = None
        self.client = None


    def _get_current_event_slug(self):
        return fetch_current_event_slug()  
    

    # --- L1 Authentication ----
    async def authenticate(self):
        """
        L1 -> L2 Method: call this ONLY when you're ready to trade.
        Uses the provided PK or pulls from config.
        """
        target_pk = self.private_key
        if not target_pk:
            raise ValueError("Private Key required for authentication")
        
        self.signer_client = ClobClient(
            host=self.clob_endpoint,
            chain_id=int(self.chain_id),
            key=target_pk,
            signature_type=0
        )
        creds = self.signer_client.create_or_derive_api_creds()
        print(f"🔐 L2 Auth Successful for Key: {creds}...")
        
        api_creds = ApiCreds(
                api_key=creds.api_key,
                api_secret=creds.api_secret,
                api_passphrase=creds.api_passphrase
            )
        self.client = ClobClient(
                host = self.clob_endpoint,
                chain_id=int(self.chain_id),
                key=self.private_key,
                creds=api_creds,
                signature_type=2,
                funder=self.funder_address
            )
        

        
        print("🔐 L2 Initialization Complete. Ready to trade.")



    # --------L2 methods------------
    
    # create_orders
    def create_order(self,order_args):
        if not self.client:
            print("❌ Error: Client not authenticated. Call authenticate() first.")
            return        
        return self.client.create_order(order_args)
    
    async def create_market_order(self,order_args):
        if not self.client:
            print("❌ Error: Client not authenticated. Call authenticate() first.")
            return        
        return await self.client.create_market_order(order_args)

    async def create_and_post_order(self, user_order):
        if not self.client:
            print("❌ Error: Client not authenticated. Call authenticate() first.")
            return        
        return await self.client.create_and_post_order(user_order)

    # post orders
    async def post_order(self,signed_order ):
        if not self.client:
            print("❌ Error: Client not authenticated. Call authenticate() first.")
            return
        return await self.client.post_order(signed_order)
    
    async def post_orders(self,signed_orders):
        if not self.client:
            print("❌ Error: Client not authenticated. Call authenticate() first.")
            return
        return await self.client.post_orders(signed_orders)
    
    # cancel orders
    async def cancel_order(self,order_id):
        if not self.client:
            print("❌ Error: Client not authenticated. Call authenticate() first.")
            return
        return await self.client.cancel(order_id)
    
    async def cancel_orders(self,order_ids):
        if not self.client:
            print("❌ Error: Client not authenticated. Call authenticate() first.")
            return
        return await self.client.cancel_orders(order_ids)
    
    async def cancel_market_orders(self,order_ids):
        if not self.client:
            print("❌ Error: Client not authenticated. Call authenticate() first.")
            return
        return await self.client.cancel_orders(order_ids)

    async def cancel_all(self):
        if not self.client:
            print("❌ Error: Client not authenticated. Call authenticate() first.")
            return  
        return await self.client.cancel_all()
     
    #get orders
    def get_order(self, order_id):
        if not self.client:
            print("❌ Error: Client not authenticated. Call authenticate() first.")
            return  
        return self.client.get_order(order_id)
    
    def get_orders(self, order_ids):
        if not self.client:
            print("❌ Error: Client not authenticated. Call authenticate() first.")
            return  
        return self.client.get_orders(order_ids)
    
    def get_open_orders(self, token_ids):
        if not self.client:
            print("❌ Error: Client not authenticated. Call authenticate() first.")
            return  
        return self.client.get_order_books(token_ids)
    
    def get_trades(self,trade_params):
        if not self.client:
            print("❌ Error: Client not authenticated. Call authenticate() first.")
            return  
        return self.client.get_trades(trade_params)
    
    def get_balance_allowance(self, balance_allow_params):
        if not self.client:
            print("❌ Error: Client not authenticated. Call authenticate() first.")
            return  
        return self.client.get_balance_allowance(balance_allow_params)
    
    


    # --- CLOB REST Data Fetchers ---
    async def fetch_order_book(self):
        """Returns the current buy/sell depth for a specific token"""
        url = f"{self.clob_endpoint}/book"
        return await self.clob_services.get_clob_rest(url,params={'token_id':self.clob_ids})

    async def fetch_last_price(self, side="buy"):
        """Returns the current market price for a side (buy/sell)"""

        url = f"{CLOB_ENDPOINT}/price"
        return await self.clob_services.get_clob_rest(url, params={
                "token_id":self.clob_ids, 
                "side":side
            })

    async def fetch_price_history(self, interval='1h', fidelity=1):
        """Returns the historical odds (probability) for the token"""
        
        url = f"{CLOB_ENDPOINT}/prices-history"
        return await self.clob_services.get_clob_rest(url, params={
            "market": self.clob_ids,
            "interval": interval,
            "fidelity": fidelity
        })  
