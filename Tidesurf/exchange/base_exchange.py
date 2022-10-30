

class BaseExchange(object):
    def __init__(self):
        pass

    def place_market_buy_order(self, symbol: str, price: float, quantity: float or int):
        pass

    def place_market_buy_order_async(self, symbol: str, price: float, quantity: float or int):
        pass

    def place_market_sell_order(self, symbol: str, price: float, quantity: float or int):
        pass

    def place_market_sell_order_async(self, symbol: str, price: float, quantity: float or int):
        pass
