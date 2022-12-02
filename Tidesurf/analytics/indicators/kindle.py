from Tidesurf.analytics.indicators.interval_buffer import IntervalBuffer
from typing import List
import numpy as np

"""
Kindle chart for O,C, H, L
"""


class Kindle:
    # interval of the data points, such as 5m, 1m, 1hr, in number of seconds
    interval_length: int
    start_timestamp: int

    interval_buffer: IntervalBuffer[List[np.float64]]
    # [[O, C, H, L]]
    indicator_values: List[List[np.float64]]

    def __init__(self, interval_length: int, start_timestamp: int):
        self.interval_length = interval_length
        self.start_timestamp = start_timestamp

        self.interval_buffer = IntervalBuffer(self.interval_length, self.start_timestamp)
        self.indicator_values = list()

    # price
    def append(self, timestamp: int, data: np.float64):
        if self.interval_buffer.is_outside_cur_buffer_interval(timestamp):
            interval_data = self.interval_buffer.get_buffer_data_and_advance()
            self.compute_and_append_indicator(interval_data)
            if not interval_data:
                self.append(timestamp, data)
        else:
            self.interval_buffer.append(timestamp, data)

    def compute_and_append_residual(self):
        interval_data = self.interval_buffer.get_buffer_data_and_advance()
        self.compute_and_append_indicator(interval_data)

    def get_indicator_values(self):
        return self.indicator_values

    def compute_and_append_indicator(self, interval_data):
        if interval_data:
            array = np.array(interval_data, dtype=np.float64)
            self.indicator_values.append([
                array[0],
                array[-1],
                np.max(array),
                np.min(array)
            ])
        else:
            # if having previous record, then append previous close for OCHL
            if len(self.indicator_values) > 0:
                self.indicator_values.append([
                    self.indicator_values[-1][1],
                    self.indicator_values[-1][1],
                    self.indicator_values[-1][1],
                    self.indicator_values[-1][1]
                ])
            else:
                self.indicator_values.append([
                    np.float64(0.),
                    np.float64(0.),
                    np.float64(0.),
                    np.float64(0.)
                ])
