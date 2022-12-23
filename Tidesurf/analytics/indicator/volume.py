from Tidesurf.analytics.indicator.indicator import Indicator
from typing import List, Tuple, Hashable
import numpy as np
import pandas as pd

"""
Volume data for given interval
"""


class Volume(Indicator[np.float64, np.float64]):

    def append_record(self, record_row: Tuple[Hashable, pd.Series]):
        timestamp_list = self.storage_adapter.get_timestamp(record_row)
        volume_list = self.storage_adapter.get_volume(record_row)

        for i in range(len(timestamp_list)):
            self.append(timestamp_list[i], volume_list[i])

    def compute_and_append_indicator(self, interval_data: List[np.float64]):
        if interval_data:
            array = np.array(interval_data, dtype=np.float64)
            self.indicator_values.append(np.float64(np.sum(array)))
        else:
            self.indicator_values.append(np.float64(0.))
