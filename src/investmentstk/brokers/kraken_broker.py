import base64
import hashlib
import hmac
import json
import os
import time
import urllib

import requests

# Construct the request and print the result
from investmentstk.brokers.broker import Broker


class KrakenBroker(Broker):
    """
    Request auth boilerplate from https://docs.kraken.com/rest/#section/Authentication/Headers-and-Signature
    """

    @property
    def friendly_name(self):
        return "Kraken"

    API_URL = "https://api.kraken.com"

    def __init__(self, *, skip_cache: bool = False):
        credentials = json.loads(os.environ["KRAKEN_CREDENTIALS"])
        self._api_key = credentials['api_key']
        self._private_key = credentials['private_key']

    def retrieve_stop_losses(self):
        response = self._kraken_request('/0/private/OpenOrders', {
            "nonce": str(int(1000 * time.time())),
            "trades": True
        }, self._api_key, self._private_key)

        response.raise_for_status()
        data = response.json()

        if data['error']:
            raise RuntimeError(f'Something went wrong: {data["error"]}')

        output = []

        for order in data["result"]["open"].values():
            if order["descr"]["ordertype"] != "stop-loss":
                continue

            entry = dict(
                fqn_id="KR:" + order['descr']['pair'],
                stop_loss_trigger=order['descr']['price'],
                stop_loss_valid_until=(order['expiretm'] or '2099-12-31')
            )

            output.append(entry)

        return output

    def retrieve_balance(self):
        """

        Relevant: https://medium.com/coinmonks/get-your-real-time-trade-balance-from-kraken-in-google-sheets-ca3adaed8b4

        :return:
        """
        response = self._kraken_request('/0/private/TradeBalance', {
            "nonce": str(int(1000 * time.time())),
            "asset": "ZEUR"
        }, self._api_key, self._private_key)

        response.raise_for_status()
        data = response.json()

        if data['error']:
            raise RuntimeError(f'Something went wrong: {data["error"]}')

        data = data['result']

        # eb = Equivalent balance (combined balance of all currencies)

        return {"balance": float(data["eb"]), "currency": 'EUR'}

    @classmethod
    def _get_kraken_signature(cls, urlpath, data, secret):
        postdata = urllib.parse.urlencode(data)
        encoded = (str(data['nonce']) + postdata).encode()
        message = urlpath.encode() + hashlib.sha256(encoded).digest()

        mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
        sigdigest = base64.b64encode(mac.digest())

        return sigdigest.decode()

    @classmethod
    def _kraken_request(cls, uri_path, data, api_key, api_sec):
        headers = {}

        headers['API-Key'] = api_key
        headers['API-Sign'] = cls._get_kraken_signature(uri_path, data, api_sec)

        req = requests.post((cls.API_URL + uri_path), headers=headers, data=data)

        return req
