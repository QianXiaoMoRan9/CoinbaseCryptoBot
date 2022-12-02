import numpy as np
from decimal import Decimal, ROUND_HALF_DOWN
from typing import List
from Tidesurf.trader.sticky_positions.symbol_position_config import SymbolPositionConfig


class SymbolPosition(object):
    decay_period_sec: int
    decay_factor: np.float64
    symbol: str

    positions: np.array
    precision: Decimal
    start_price: Decimal
    end_price: Decimal
    last_window_timestamp: int
    top_agg_id: int

    NULL_VALUE = Decimal("-1")
    NULL_AGG_ID = -1

    def __init__(self, config: SymbolPositionConfig):

        self.symbol = config.symbol
        self.decay_period_sec = config.decay_period_sec
        self.decay_factor = config.decay_factor

        self.last_window_timestamp = 0 # unit time start
        self.positions = np.array([])
        self.precision = Decimal(config.precision)
        self.start_price = self.NULL_VALUE
        self.end_price = self.NULL_VALUE
        self.top_agg_id = self.NULL_AGG_ID

    def add_trades(self, trades: List[List[int, int, np.float64, np.float64]]):
        """
        stream trade into buffer first, if buffer time exceeds the minimum time
        [
            [
                agg_id,
                timestamp,
                price,
                volume
            ]
        ]
        """
        for trade in trades:
            self.add_trade(trade)

    def add_trade(self, trade: List[int, int, np.float64, np.float64]):
        [agg_id, timestamp, price, volume] = trade
        price_decimal = self._float_to_decimal(price)
        # check if position array exists
        if self.start_price == self.NULL_VALUE and self.end_price == self.NULL_VALUE:
            self.start_price, self.end_price = price_decimal, price_decimal
            self.positions = np.array([volume], dtype=np.float64)
        # position array already exists
        else:
            # check if the new timestamp lies in a new decay window:
            if timestamp - self.last_window_timestamp > self.decay_period_sec:
                decay_exponent = (timestamp - self.last_window_timestamp) // self.decay_period_sec
                self.positions * (self.decay_factor ** decay_exponent)
            # Add new trade into the position
            if self.start_price <= price_decimal <= self.end_price:
                index = self._get_price_index(price_decimal)
                self.positions[index] += volume
            elif price_decimal < self.start_price:
                # pad left with price at the left most
                padding = np.zeros(((self.start_price - price_decimal) // self.precision,), dtype=np.float64)
                padding[0] = price
                self.positions = np.concatenate([padding, self.positions], axis=0)
                self.start_price = price_decimal
            else:
                # pad right with price at the right most
                padding = np.zeros(((price_decimal - self.end_price) // self.precision,), dtype=np.float64)
                padding[-1] = price
                self.positions = np.concatenate([self.positions, padding], axis=0)
                self.end_price = price_decimal
            self.top_agg_id = max(self.top_agg_id, agg_id)
        self._update_last_window_timestamp(timestamp)

    def _get_price_index(self, price: Decimal or np.float4 or float):
        if type(price) != Decimal:
            price = self._float_to_decimal(price)
        return (price - self.start_price) // self.precision

    def _float_to_decimal(self, f: str or float or np.float64) -> Decimal:
        return Decimal(f).quantize(self.precision, rounding=ROUND_HALF_DOWN)

    def _update_last_window_timestamp(self, timestamp):
        self.last_window_timestamp = ((timestamp - self.last_window_timestamp) // self.decay_period_sec) * self.decay_period_sec + self.last_window_timestamp