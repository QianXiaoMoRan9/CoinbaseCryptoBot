from typing import List
from typing import Tuple, Hashable

import numpy as np
import pandas as pd

from Tidesurf.analytics.indicator.indicator import Indicator
from Tidesurf.data.storage_adapters.storage_adapter import StorageAdapter
from Tidesurf.trader.trader import Trader

"""
Exponential moving average for a given period

NUM_INTERVAL = 5

SMOOTHING = 2

EMA_t0 = AVG(PRICE among NUM_INTERVAL periods)

MULTIPLIER = SMOOTHING/(1 + NUM_INTERVAL)

EMA_t = PRICE_t * MULTIPLIER + EMA_t-1 * (1 - MULTIPLIER)
"""


class EMA(Indicator[List[np.float64], np.float64]):
    smoothing: int
    num_interval: int

    multiplier: np.float64

    ZERO_PRICE = np.float64(0.)

    def __init__(
            self,
            trader: Trader,
            storage_adapter: StorageAdapter,
            interval_length: int,
            start_timestamp: int,
            num_interval: int,
            smoothing: int = 2):
        super().__init__(trader, storage_adapter, interval_length, start_timestamp)
        self.smoothing = smoothing
        self.num_interval = num_interval

        self.multiplier = np.float64(smoothing / (1 + self.num_interval))
        print("Got multiplier ", self.multiplier)
        self.average_prices = list()

    def append_record(self, record_row: Tuple[Hashable, pd.Series]):
        timestamp_list = self.storage_adapter.get_timestamp(record_row)
        price_list = self.storage_adapter.get_price(record_row)
        volume_list = self.storage_adapter.get_volume(record_row)

        for i in range(len(timestamp_list)):
            self.append(timestamp_list[i], [price_list[i], volume_list[i]])

    # [price, volume]
    def compute_and_append_indicator(self, interval_data: List[List[np.float64]]):
        average_price = EMA.ZERO_PRICE
        if interval_data:
            array = np.array(interval_data)
            price_array = array[:, 0]
            volume_array = array[:, 1]
            average_price = np.sum(price_array * volume_array) / np.sum(volume_array)
        # We skip computing zero value
        if len(self.indicator_values) < self.num_interval - 1:
            self.indicator_values.append(average_price)
        elif len(self.indicator_values) == self.num_interval - 1:
            self.indicator_values.append(average_price)
            s = np.float64(0)
            num_non_zero_value = 0
            for value in self.indicator_values:
                if value != self.ZERO_PRICE:
                    s += value
                    num_non_zero_value += 1
            if num_non_zero_value == 0:
                raise Exception(
                    f"""Provided interval and starting timestamp does not have any trades, please adjust. Interval: {self.interval_length}, start_timestamp: {self.start_timestamp}""")
            average_price = s / num_non_zero_value
            for i in range(self.num_interval):
                self.indicator_values[i] = average_price
            print("Finished constructing top average, ", self.indicator_values)
        else:
            if average_price == self.ZERO_PRICE:
                average_price = self.average_prices[-1]
            ema_t0 = self.indicator_values[-1]
            ema_t = average_price * self.multiplier + ema_t0 * (1 - self.multiplier)
            self.indicator_values.append(ema_t)
        self.average_prices.append(average_price)
