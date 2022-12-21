from typing import List

import numpy as np

from Tidesurf.analytics.indicators.indicator import Indicator

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

    def __init__(self, interval_length: int, num_interval: int, start_timestamp: int, smoothing: int = 2):
        super().__init__(interval_length, start_timestamp)
        self.smoothing = smoothing
        self.num_interval = num_interval

        self.multiplier = np.float64(smoothing / (1 + self.num_interval))
        print("Got multiplier ", self.multiplier)
        self.average_prices = list()

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
