from abc import ABC, abstractmethod

from Tidesurf.database.enums import TradeMode
from Tidesurf.trader.trader import Trader


class ExchangeAdapter(ABC):

    trader: Trader
    trade_mode: TradeMode
    def __init__(self, trader: Trader, trade_mode: TradeMode):
        self.trader = trader
        self.trade_mode = trade_mode

    @abstractmethod
    @property
    def exchange_name(self):
        pass

    @abstractmethod
    def place_market_buy_order(self, symbol: str, price: float, quantity: float or int):
        pass

    @abstractmethod
    def place_market_buy_order_async(self, symbol: str, price: float, quantity: float or int):
        pass

    @abstractmethod
    def place_market_sell_order(self, symbol: str, price: float, quantity: float or int):
        pass

    @abstractmethod
    def place_market_sell_order_async(self, symbol: str, price: float, quantity: float or int):
        pass
