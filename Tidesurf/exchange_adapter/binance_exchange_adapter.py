from Tidesurf.database.enums import TradeMode, TradeType, TradeSide
from Tidesurf.exchange_adapter.exchange_adapter import ExchangeAdapter
from Tidesurf.trader.trader import Trader
import os
import urllib.parse
import hashlib
import hmac
import requests
import time


class BinanceExchangeAdapter(ExchangeAdapter):
    API_KEY = os.environ.get("BINANCE_API_KEY")
    SECRET_KEY = os.environ.get("BINANCE_SECRET_KEY")
    API_URL = "https://api.binance.us"

    ORDER_API_PATH = "/api/v3/order"
    ORDER_API_PATH_TEST = "/api/v3/order/test"

    def __init__(self, trader: Trader, trade_mode: TradeMode):
        super().__init__(trader, trade_mode)

    @property
    def exchange_name(self):
        return "Binance.US"

    def place_market_buy_order(self, symbol: str, price: float, quantity: float or int):
        if self.trade_mode == TradeMode.BACK_TESTING:
            # BinanceExchangeAdapter.
            pass
        elif self.trade_mode == TradeMode.DRY_RUN:
            BinanceExchangeAdapter._place_market_buy_order_dryrun(symbol, quantity)
        elif self.trade_mode == TradeMode.LIVE:
            BinanceExchangeAdapter._place_market_buy_order_live(symbol, quantity)
        else:
            raise Exception("TradeMode not supported")

    @staticmethod
    def _place_market_buy_order_live(symbol, quantity):
        data = {
            "symbol": symbol,
            "side": TradeSide.BUY,
            "type": TradeType.MARKET,
            "quantity": quantity,
            "timestamp": int(round(time.time() * 1000))
        }
        return BinanceExchangeAdapter._place_order_live(data)

    @staticmethod
    def _place_market_buy_order_dryrun(symbol, quantity):
        data = {
            "symbol": symbol,
            "side": TradeSide.BUY,
            "type": TradeType.MARKET,
            "quantity": quantity,
            "timestamp": int(round(time.time() * 1000))
        }
        return BinanceExchangeAdapter._place_order_dryrun(data)



    @staticmethod
    def _place_order_live(data):
        return BinanceExchangeAdapter._binanceus_request(
            BinanceExchangeAdapter.ORDER_API_PATH,
            data,
            BinanceExchangeAdapter.API_KEY,
            BinanceExchangeAdapter.SECRET_KEY)

    @staticmethod
    def _place_order_dryrun(data):
        return BinanceExchangeAdapter._binanceus_request(
            BinanceExchangeAdapter.ORDER_API_PATH_TEST,
            data,
            BinanceExchangeAdapter.API_KEY,
            BinanceExchangeAdapter.SECRET_KEY)

    @staticmethod
    def _get_binanceus_signature(data, secret):
        postdata = urllib.parse.urlencode(data)
        message = postdata.encode()
        byte_key = bytes(secret, 'UTF-8')
        mac = hmac.new(byte_key, message, hashlib.sha256).hexdigest()
        return mac

    @staticmethod
    def _binanceus_request(uri_path, data, api_key, api_sec):
        headers = dict()
        headers['X-MBX-APIKEY'] = api_key
        signature = BinanceExchangeAdapter._get_binanceus_signature(data, api_sec)
        payload = {
            **data,
            "signature": signature,
        }
        req = requests.post((BinanceExchangeAdapter.API_URL + uri_path), headers=headers, data=payload)
        return req.text
