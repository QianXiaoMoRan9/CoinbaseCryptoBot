"""
Make trading decision and call the order execution API

It maintains:
- Its own strategy parameters
- Current positions
- Current market positions
- Current pending orders

It takes in continuous feed of data:
- Order tick
- Order book
- Any other market data factors

It calls:
- Pricing modules to get pricing and make decision of whether to trade
- Broker API to submit order
- Broker API to submit cancel order if it is not filled

"""
class BaseTrader(object):
    precision: int
    def __init__(self, precision):
        self.precision = precision

    """
    Callback when there is market data updates

    Takes in the market updated data
    Update internal states
    Make decision on whether to make trades
    """

    def handle_market_update(self, *args, **kwargs):
        raise NotImplementedError("handle_market_update is not implemented")

    """
    Callback when there is a order submission updates
    """
    def handle_order_update(self, *args, **kwargs):
        raise NotImplementedError("handle_order_update is not implemented")
