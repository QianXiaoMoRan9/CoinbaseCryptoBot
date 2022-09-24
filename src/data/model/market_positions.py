from dataclasses import dataclass
import numpy as np
import math

"""
市场在一个时间区间之内的头寸分布情况
"""
@dataclass
class MarketPositions(object):
    start_timestamp: int
    end_timestamp: int
    # 10 ^ (-precision) as the incremental step for the number
    precision: int
    """
    Consecutive price volume pairs
    [
        [10.01, 100],
        [10.02, 0],
        [10.03, 105.8],
        [10.04, 6.0],
        ....
        [11.57, 19.0]
    ]
    """
    # [10.01, 10.02, 10.03,...]
    prices: np.ndarray
    # [100, 0, 105.8, 6.0, ...]
    positions: np.ndarray

    def get_step(self) -> float:
        return 10**(-self.precision)

    def compute_position_distributions(self) -> np.ndarray:
        total_positions = np.sum(self.positions)
        return self.total_positions / total_positions

    def get_num_prices(self) -> int:
        return self.prices.shape[0]

    def get_index_from_price(self, price: float) -> int:
        if (price < self.prices[0] or price > self.prices[-1]):
            return -1
        index = math.floor((price - self.prices[0]) / self.get_step())
        assert index < self.prices.shape[0], "Index should not exceed the max value"
        return index