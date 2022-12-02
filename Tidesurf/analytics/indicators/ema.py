from Tidesurf.analytics.indicators.interval_buffer import IntervalBuffer
from typing import List
import numpy as np

"""
Exponential moving average for a given period

NUM_INTERVAL = 5

SMOOTHING = 2

EMA_t0 = AVG(PRICE among NUM_INTERVAL periods)

MULTIPLIER = SMOOTHING/(1 + NUM_INTERVAL)

EMA_t = PRICE_t * MULTIPLIER + EMA_t-1 * (1 - MULTIPLIER)
"""

class EMA:
    # interval of the data points, such as 5m, 1m, 1hr, in number of seconds
    interval_length: int
    smoothing: int
    num_interval: int
    start_timestamp: int

    multiplier: np.float64

    interval_buffer: IntervalBuffer[List[List[np.float64]]]
    indicator_values: List[np.float64]

    ZERO_PRICE = np.float64(0.)

    def __init__(self, interval_length: int, num_interval: int, start_timestamp: int, smoothing: int = 2):
        self.interval_length = interval_length
        self.smoothing = smoothing
        self.num_interval = num_interval
        self.start_timestamp = start_timestamp

        self.multiplier = np.float64(smoothing / (1 + self.num_interval))
        print("Got multiplier ", self.multiplier)
        self.average_prices = list()
        self.indicator_values = list()
        self.interval_buffer = IntervalBuffer(self.interval_length, self.start_timestamp)

    # [price, volume]
    def append(self, timestamp: int, data: List[np.float64]):
        if self.interval_buffer.is_outside_cur_buffer_interval(timestamp):
            interval_data = self.interval_buffer.get_buffer_data_and_advance()
            self.compute_and_append_indicator(interval_data)
            if not interval_data:
                self.append(timestamp, data)
        else:
            self.interval_buffer.append(timestamp, data)

    def compute_and_append_indicator(self, interval_data):
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
