from Tidesurf.pricing.base_pricing import BasePricing
from Tidesurf.data.model.tick import Tick
from Tidesurf.data.model.market_positions import MarketPositions
import numpy as np

"""
Stickiness == position distribution (% of position at this price point)
"""


class NaiveStickyPositionPricing(BasePricing):
    def __init__(self, market_positions: MarketPositions):
        super().__init__(market_positions)
        self._market_positions = market_positions
        self._position_distribution = self._market_positions.compute_position_distributions()

    def compute_target_price_and_stop_loss(self, cur_tick: Tick) -> tuple[
        np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        distribution_sort = np.argsort(self._position_distribution)

        target_price_list = list()
        stop_loss_list = list()
        target_price_probability_list = list()
        stop_loss_probability_list = list()

        for index in range(distribution_sort.shape[0]):
            target_price = self._market_positions.prices[index]
            profit = target_price - cur_tick.price
            if profit >= 0.:
                target_price_list.append(target_price)
                target_price_probability_list.append(self._position_distribution[index])
            else:
                stop_loss_list.append(profit)
                stop_loss_probability_list.append((profit))
        return np.array(target_price_list), np.array(target_price_probability_list), np.array(stop_loss_list), np.array(
            stop_loss_probability_list)

    def compute_max_position_to_take(self, cur_tick: Tick) -> float:
        expected_gain = self._compute_expected_gain_from_cur_tick(cur_tick)
        if (expected_gain <= 0.0):
            return 0.0
        return 0.05

    """
    Percentage of gain given entering at cur_tick
    """

    def _compute_expected_gain_from_cur_tick(self, cur_tick: Tick) -> float:
        total_gain = 0
        # index greater is gain:
        for index in range(0, self._market_positions.get_num_prices()):
            total_gain += (self._market_positions.prices[index] - cur_tick.price) * self._position_distribution[index]
        return total_gain / cur_tick.price
