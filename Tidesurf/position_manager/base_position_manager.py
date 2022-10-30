from Tidesurf.data.model.position_map import PositionMap
from Tidesurf.data.model.position import Position
import numpy as np

from typing import List


class BasePositionManager(object):
    REJECT_QUANTITY = None
    position_map: PositionMap
    cash: np.float64

    def __init__(self, current_cash: np.float64, current_positions: List[Position]):
        self.cash = current_cash
        self.position_map = PositionMap.from_position_list(current_positions)

    def get_product_positions(self, symbol: str) -> List[Position]:
        return self.position_map.get_product_positions(symbol)

    def add_position(self, position):
        self.position_map.add_position(position)

    def remove_position(self, position):
        self.position_map.remove_position(position)

    """
    Return the quantity of share worth of cash reserved according to percentage and price
    """
    def reserve_quantity(self, price: np.float64, percentage: np.float64) -> int:
        raise NotImplementedError("WIP")
        return REJECT_QUANTITY


    def is_valid_quantity(self, quantity: float or int or None):
        return quantity is not None
