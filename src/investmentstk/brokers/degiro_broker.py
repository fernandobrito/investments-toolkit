import datetime
import json
import os
from degiro_connector.trading.api import API as TradingAPI
from degiro_connector.trading.models.trading_pb2 import Credentials, Update, Order

from investmentstk.brokers.broker import Broker
from investmentstk.models import StopLoss, BrokerBalance
from investmentstk.persistence.requests_cache import requests_cache_configured


class DegiroBroker(Broker):
    @property
    def friendly_name(self):
        return "Degiro"

    def __init__(self, skip_cache: bool = None):
        credentials = json.loads(os.environ["DEGIRO_CREDENTIALS"])

        credentials = Credentials(
            int_account=credentials["int_account"],
            username=credentials["username"],
            password=credentials["password"],
            totp_secret_key=credentials["totp_secret_key"],
        )

        self.api_client = TradingAPI(credentials=credentials)
        self.api_client.connect()

    @requests_cache_configured(hours=0.5)
    def retrieve_balance(self) -> BrokerBalance:
        request_list = Update.RequestList()
        request_list.values.extend(
            [
                Update.Request(option=Update.Option.TOTALPORTFOLIO, last_updated=0),
            ]
        )

        response = self.api_client.get_update(request_list=request_list, raw=True)
        entry = next(entry for entry in response["totalPortfolio"]["value"] if entry["name"] == "reportNetliq")

        return BrokerBalance(balance=entry["value"], currency="SEK")

    @requests_cache_configured(hours=0.5)
    def retrieve_stop_losses(self) -> list[StopLoss]:
        request_list = Update.RequestList()
        request_list.values.extend(
            [
                Update.Request(option=Update.Option.ORDERS, last_updated=0),
            ]
        )

        orders = self.api_client.get_update(request_list=request_list).orders

        output = []

        for order in orders.values:
            if order.order_type != Order.OrderType.STOP_LOSS:
                continue

            output.append(self._format_stop_loss(order))

        return output

    @staticmethod
    def _format_stop_loss(order: Order) -> StopLoss:
        if order.time_type == Order.TimeType.GOOD_TILL_CANCELED:
            valid_until = "2099-12-31"
        elif order.time_type == Order.TimeType.GOOD_TILL_DAY:
            valid_until = datetime.date.today().isoformat()
        else:
            raise RuntimeError(f"Unknown time_type on Degiro order: {order.time_type}")

        # TODO: Avoid hardcoding DG here
        return StopLoss(
            fqn_id="DG:" + str(order.product_id), trigger=order.stop_price, valid_until=valid_until  # type: ignore
        )
