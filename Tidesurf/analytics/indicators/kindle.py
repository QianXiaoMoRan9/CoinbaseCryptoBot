from typing import List

import numpy as np

from Tidesurf.analytics.indicators.indicator import Indicator

"""
Kindle chart for O,C, H, L
"""


class Kindle(Indicator[np.float64, List[np.float64]]):

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
