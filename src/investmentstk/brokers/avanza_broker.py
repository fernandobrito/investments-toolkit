from __future__ import absolute_import  # type: ignore

import json
import os

from avanza import Avanza

from investmentstk.brokers.broker import Broker
from investmentstk.models import StopLoss, BrokerBalance
from investmentstk.persistence.requests_cache import requests_cache_configured


class AvanzaBroker(Broker):
    @property
    def friendly_name(self):
        return "Avanza"

    def __init__(self, *, skip_cache: bool = False):
        credentials = json.loads(os.environ["AVANZA_CREDENTIALS"])

        # 1/20 = 3 minutes, as too many hits on the Avanza authentication
        # API will start failing and they actually block your password authentication
        # for 5 minutes
        hours_cache = 1 / 20 if skip_cache else 1

        with requests_cache_configured(
            hours=hours_cache, allowable_methods=["GET", "HEAD", "POST"], ignored_parameters=["totpCode"]
        ):
            self._client = Avanza(
                {
                    "username": credentials["username"],
                    "password": credentials["password"],
                    "totpSecret": credentials["totpSecret"],
                }
            )

    def retrieve_balance(self) -> BrokerBalance:
        account_id = str(os.environ["AVANZA_ACCOUNT_ID"])

        account_overview = self._client.get_account_overview(account_id)
        balance = (
            account_overview["totalPositionsValue"]
            + account_overview["totalBalance"]
            + account_overview["creditAccountBalance"]
        )

        return BrokerBalance(balance=balance, currency="SEK")

    def retrieve_stop_losses(self) -> list[StopLoss]:
        output = []

        for stop_loss in self._client.get_all_stop_losses():
            fqn_id = "AV:" + stop_loss["orderbook"]["id"]
            trigger = stop_loss["trigger"]["value"]
            valid_until = stop_loss["trigger"]["validUntil"]

            entry = StopLoss(fqn_id=fqn_id, trigger=trigger, valid_until=valid_until)

            output.append(entry)

        return output
