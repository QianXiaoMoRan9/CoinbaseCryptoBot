from typing import List, TypeVar, Generic

BufferData = TypeVar('BufferData')


class IntervalBuffer(Generic[BufferData]):
    # length of interval in seconds
    interval_length: int
    # Very start of data accumulation
    start_timestamp: int

    interval_data: List[BufferData]

    def __init__(self, interval_length: int, start_timestamp):
        self.interval_length = interval_length
        self.start_timestamp = start_timestamp
        self.interval_data = list()

    def append(self, timestamp: int, data: BufferData):
        assert not self.is_outside_cur_buffer_interval(timestamp), "Provided data are outside the current timestamp"
        self.interval_data.append(data)

    def get_buffered_data(self) -> List[BufferData]:
        return self.interval_data

    def get_buffer_data_and_advance(self) -> List[BufferData]:
        tmp = self.interval_data
        self.interval_data = list()
        self.start_timestamp += self.interval_length
        return tmp

    def is_outside_cur_buffer_interval(self, timestamp: int) -> bool:
        return (timestamp - self.start_timestamp) > self.interval_length
