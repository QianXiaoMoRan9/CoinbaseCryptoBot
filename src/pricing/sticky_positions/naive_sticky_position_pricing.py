from pricing.base_pricing import BasePricing
from data.model.tick import Tick
from data.model.market_positions import MarketPositions
import numpy as np
from typing import List

"""
Stickiness == position distribution (% of position at this price point)
"""
class NaiveStickyPositionPricing(BasePricing):
    def __init__(self, market_positions: MarketPositions):
        self._market_positions = market_positions
        self._position_distribution = self._market_positions.compute_position_distributions()

    def compute_target_price_and_stop_loss(self, cur_tick: Tick, limit: int = 3) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        expected_gain = self._compute_expected_gain_from_cur_tick(cur_tick)
        if (expected_gain <= 0.0):
            return (np.array([]), np.array([]), np.array([]))
        
        # Compute top 3 probability among the profitable price range
        cur_price_index = self._market_positions.get_index_from_price(cur_tick.price)
        distribution_slice = self._position_distribution[cur_price_index:]
        distribution_sort = np.argsort(distribution_slice)[: limit]

        target_price_list = list()
        stop_loss_list = list()
        target_price_brobability_list = list()

        for index in range(distribution_sort.shape[0]):
            price_index = distribution_sort[index] + cur_price_index
            target_price = self._market_positions.prices[price_index]
            target_price_list.append(target_price)

            profit = target_price - cur_tick.price
            stop_loss_list.append(cur_tick.price - profit)
            target_price_brobability_list.append(distribution_slice[price_index])
            
        return (np.array(target_price_list), np.array(stop_loss_list), np.array(target_price_brobability_list))
    
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
        for index in range(0, self._market_positions.get_num_prices):
            total_gain += (self._market_positions.prices[index] - cur_tick.price) * self._position_distribution[index]
        return total_gain / cur_tick.price
