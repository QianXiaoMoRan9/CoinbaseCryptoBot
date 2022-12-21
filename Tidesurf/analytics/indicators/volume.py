from Tidesurf.analytics.indicators.indicator import Indicator
from typing import List
import numpy as np

"""
Volume data for given interval
"""


class Volume(Indicator[np.float64, np.float64]):

    def compute_and_append_indicator(self, interval_data: List[np.float64]):
        if interval_data:
            array = np.array(interval_data, dtype=np.float64)
            self.indicator_values.append(np.float64(np.sum(array)))
        else:
            self.indicator_values.append(np.float64(0.))
