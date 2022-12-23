from abc import ABC, abstractmethod
from Tidesurf.analytics.indicator.interval_buffer import IntervalBuffer
from Tidesurf.data.storage_adapters.storage_adapter import StorageAdapter
from typing import TypeVar, Generic, List, Hashable, Tuple
import pandas as pd

INDICATOR_INPUT_TYPE = TypeVar("INDICATOR_INPUT_TYPE")
INDICATOR_TYPE = TypeVar("INDICATOR_TYPE")


class Indicator(ABC, Generic[INDICATOR_INPUT_TYPE, INDICATOR_TYPE]):
    storage_adapter: StorageAdapter
    # interval of the data points, such as 5m, 1m, 1hr, in number of seconds
    interval_length: int
    start_timestamp: int

    interval_buffer: IntervalBuffer[INDICATOR_INPUT_TYPE]
    indicator_values: List[INDICATOR_TYPE]

    def __init__(
            self,
            storage_adapter: StorageAdapter,
            interval_length: int,
            start_timestamp: int):
        self.storage_adapter = storage_adapter
        self.interval_length = interval_length
        self.start_timestamp = start_timestamp

        self.interval_buffer = IntervalBuffer(self.interval_length, self.start_timestamp)
        self.indicator_values = list()

    def append(self, timestamp: int, data: INDICATOR_INPUT_TYPE):
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

    def get_indicator_values(self) -> List[INDICATOR_TYPE]:
        return self.indicator_values

    @abstractmethod
    def append_record(self, record_row: Tuple[Hashable, pd.Series]):
        pass

    @abstractmethod
    def compute_and_append_indicator(self, interval_data: List[INDICATOR_INPUT_TYPE]):
        pass
