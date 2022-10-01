from Tidesurf.trader.base_trader import BaseTrader

class FixStopLossBasicTrader(BaseTrader):
    def __init__(self):
        super().__init__(self)

    """
    Callback when there is market data updates
    
    Takes in the market updated data
    Update internal states
    Make decision on whether to make trades
    """
    def handle_market_update(self, ):
        pass

    """
    Callback when there is a order submission updates
    """
    def handle_order_update(self,):
        pass


