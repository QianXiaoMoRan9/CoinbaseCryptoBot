from Tidesurf.trader.base_trader import BaseTrader
from Tidesurf.data.model.tick import Tick
from Tidesurf.data.model.order_book import OrderBook
from Tidesurf.data.model.position import Position
from Tidesurf.data.model.position_map import PositionMap
from Tidesurf.data.model.market_positions import MarketPositions

class FixStopLossBasicTrader(BaseTrader):
    position_map: PositionMap
    market_positions: MarketPositions
    def __init__(self, market_positions: MarketPositions, precision: int):
        super().__init__(precision)
        self.position_map = PositionMap()
        self.market_positions = market_positions

    """
        Call pricing, if there is:
        - a profit expectation of greater than 5%
        - a first stop loss 
    """
    def handle_market_update(self, cur_tick: Tick, order_book: OrderBook):
        # update market position
        pass

    """
    Callback when there is a order submission updates
    """
    def handle_order_update(self,):
        pass


