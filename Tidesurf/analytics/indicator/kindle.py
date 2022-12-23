from typing import List, Tuple, Hashable

import numpy as np
import pandas as pd
from Tidesurf.analytics.indicator.indicator import Indicator

"""
Kindle chart for O, C, H, L
"""


class Kindle(Indicator[np.float64, List[np.float64]]):

    def append_record(self, record_row: Tuple[Hashable, pd.Series]):
        timestamp_list = self.storage_adapter.get_timestamp(record_row)
        price_list = self.storage_adapter.get_price(record_row)

        for i in range(len(timestamp_list)):
            self.append(timestamp_list[i], price_list[i])

    def compute_and_append_indicator(self, interval_data: List[np.float64]):
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
