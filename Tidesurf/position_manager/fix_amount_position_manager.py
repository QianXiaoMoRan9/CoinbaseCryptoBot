import math

import numpy as np

from Tidesurf.database.model import Cash
from Tidesurf.position_manager.position_manager import PositionManager
from Tidesurf.position_manager.position_manager import synchronized

"""
Overall position manager that manages the overall positions of each traded instruments

This position manager grants the fixed amount on each instrument for every trade:

such as $5000 per trade on any form of instrument.

If the instrument does not accept partials that can meet the amount,
then round down to the nearest amount of instrument.

"""


class FixAmountPositionManager(PositionManager):
    # fixed amount of money given out per trade
    fixed_amount: float
    # Fixed percentage of total exposed positions, including booked but not filled
    cap_percentage: float

    def __init__(self, fixed_amount: float, cap_percentage: float):
        super().__init__()
        self.fixed_amount = fixed_amount
        self.cap_percentage = cap_percentage

    @synchronized
    def get_instrument_quantity(self, price: float or np.float64, accept_partial: bool) -> float:
        cash = Cash.get_cash()

        if cash < self.fixed_amount:
            return self.REJECT_QUANTITY

        if accept_partial:
            Cash.update_cash(cash - self.fixed_amount)
            return self.fixed_amount / price
        amount = int(math.floor(self.fixed_amount / price))
        if amount == 0:
            return self.REJECT_QUANTITY
        purchase_amount = amount * price
        Cash.update_cash(cash - purchase_amount)
        return purchase_amount
