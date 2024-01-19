import hashlib
import hmac
import json
import requests
import time

class Bitfinex:

    def __init__(self, api_key: str, api_secret_key: str, url="https://api.bitfinex.com/"):
        self.__url = url
        self.__api_key = api_key
        self.__api_secret_key = api_secret_key

    def sign(self, path: str, nonce: str, data: str):
        payload = f"/api/{path}{nonce}{data.decode('utf-8')}"
        signature = hmac.new(bytes(self.__api_secret_key, 'utf-8'), bytes(payload, 'utf-8'), hashlib.sha384)
        return signature.hexdigest()

    def call(self, method: str, path: str, data=None, params=None):
        body = json.dumps(data).encode('utf-8')
        nonce = str(int(time.time() * 1000))

        headers = {
            'Content-Type': 'application/json',
            'bfx-nonce': nonce,
            'bfx-apikey': self.__api_key,
            'bfx-signature': self.sign(path, nonce, body),
        }
        response = requests.request(method.upper(), self.__url + path, headers=headers, params=params, data=body)
        response.raise_for_status()
        return response.json()

    def deposit_address(self, method='', wallet="exchange"):
        if not method:
            method = 'bitcoin'

        data = {
            "wallet": wallet,
            "method": method,
            "op_renew": 0
        }
        return self.call("POST", "v2/auth/w/deposit/address", data)

    def create_invoice(self, amount):
        data = {"currency": "LNX", "wallet": "exchange", "amount": amount}
        return self.call("POST", "v2/auth/w/deposit/invoice", data)

    def get_wallets(self):
        data = {}
        return self.call("POST", "v2/auth/r/wallets", data)

    def movements(self, currency: str = "BTC", start=0, end=0, limit=0):
        data = dict()
        if start:
            data["start"] = start
        if end:
            data["end"] = end
        if limit:
            data["limit"] = limit
        return self.call("POST", f"v2/auth/r/movements/{currency}/hist", data=data)

    def order_submit(self, symbol, amount):
        data = {"symbol": symbol, "amount": amount, "type": "EXCHANGE"}
        return self.call("POST", "v2/auth/w/order/submit", data)