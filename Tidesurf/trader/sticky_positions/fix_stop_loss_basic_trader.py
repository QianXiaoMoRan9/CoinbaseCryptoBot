import numpy as np
from typing import List
from Tidesurf.trader.bas_trader import BaseTrader
from Tidesurf.exchange.base_exchange import BaseExchange
from Tidesurf.data.model.tick import Tick
from Tidesurf.data.model.order_book import OrderBook
from Tidesurf.data.model.position import Position
from Tidesurf.pricing.base_pricing import BasePricing
from Tidesurf.position_manager.base_position_manager import BasePositionManager
from Tidesurf.data.model.market_positions import MarketPositions
from Tidesurf.data.model.decimal import PreciseDecimal
from Tidesurf.utils.number_utils import float_almost_equal

class FixStopLossBasicTrader(BaseTrader):
    symbol: str
    position_manager: BasePositionManager
    market_positions: MarketPositions
    buy_threshold: np.float64
    def __init__(self,
                 symbol: str,
                 exchange: BaseExchange,
                 market_positions: MarketPositions,
                 pricing: BasePricing,
                 current_positions: List[Position],
                 current_cash: PreciseDecimal,
                 precision: int,
                 buy_threshold: np.float64 = np.float64(0.05)):
        super().__init__(exchange, pricing, precision)
        self.symbol = symbol
        self.position_manager = BasePositionManager(current_cash, current_positions)
        self.market_positions = market_positions
        self.buy_threshold = np.float64(buy_threshold)

    """
        Call pricing, if there is:
        - a profit expectation of greater than 5%
        - a first stop loss 
    """
    def handle_market_update(self, cur_tick: Tick, order_book: OrderBook):
        # Scan through all the current positions, exit positions if needed
        current_product_positions = self.position_manager.get_product_positions(self.symbol)
        for current_position in current_product_positions:
            if current_position.stop_loss.to_float() >= cur_tick.price:
                self.exchange.place_market_sell_order(self.symbol, cur_tick.price, current_position.volume)
                self.position_manager.remove_position(current_position)

        # Compute pricing for the given market position
        target_prices, target_prices_prob, stop_losses, stop_losses_prob = \
            self.pricing.compute_target_price_and_stop_loss(cur_tick)

        expected_earnings = np.sum(target_prices * target_prices_prob)
        expected_losses = np.sum(stop_losses * stop_losses_prob)
        expected_profit = expected_earnings - expected_losses
        profit_percentage = expected_profit / cur_tick.price
        if (profit_percentage > self.buy_threshold):
            max_position_in_percentage = self.pricing.compute_max_position_to_take(cur_tick)
            # TODO: this is currently using cur_tick_price, we should base this on OrderBook
            reserved_quantity = self.position_manager.reserve_quantity(cur_tick.price, max_position_in_percentage)
            if self.position_manager.is_valid_quantity(reserved_quantity):
                self.exchange.place_market_buy_order(self.symbol, cur_tick.price, reserved_quantity)
                new_position = Position(
                    symbol=self.symbol,
                    price=PreciseDecimal.from_float_precise(cur_tick.price),
                    volume=PreciseDecimal.from_float_precise(reserved_quantity),
                    stop_loss=PreciseDecimal.from_float_precise(stop_losses[0]),
                    target_price=PreciseDecimal(target_prices[0]))
                self.position_manager.add_position(new_position)
            else:
                print("Reserved quantity rejected")

    """
    Callback when there is a order submission updates
    """
    def handle_order_update(self,):
        pass


