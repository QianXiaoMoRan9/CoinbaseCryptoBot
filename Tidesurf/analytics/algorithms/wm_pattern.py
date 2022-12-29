from typing import List, Callable

import numpy as np
import numpy.typing as npt
from scipy.signal import find_peaks

from Tidesurf.analytics.algorithms.algorithm import Algorithm
from Tidesurf.analytics.algorithms.wm import W
from Tidesurf.trader.trader import Trader


class WPattern(Algorithm[np.float64, W, np.float64]):
    # minimum percentage that low and high are different w.r.t. low
    low_high_diff_threshold_percentage: np.float64

    def __init__(self, trader: Trader, low_high_diff_threshold_percentage: np.float64):
        super().__init__(trader)
        self.low_high_diff_threshold_percentage = low_high_diff_threshold_percentage

    # 1D numpy array of an indicator sequence
    def get_all_candidates(self, x: npt.NDArray[np.float64], index_to_timestamp: Callable[[int], int]) -> List[W]:
        res = list()
        x_neg = x * -1
        peak_index_list, _ = find_peaks(x, distance=5)
        bottom_index_list, _ = find_peaks(x_neg, distance=5)
        # w shape consist of:
        # h1, l1, h2, l2, (potential h3)

        for h1_i_i in range(len(peak_index_list)):
            h1_i = peak_index_list[h1_i_i]
            h1 = x[h1_i]
            for l1_i_i in range(len(bottom_index_list)):
                l1_i = bottom_index_list[l1_i_i]
                l1 = x[l1_i]
                if self._satisfy_high_to_low_diff(h1, l1):
                    for h2_i_i in range(h1_i_i, len(peak_index_list)):
                        h2_i = peak_index_list[h2_i_i]
                        h2 = x[h2_i]
                        if self._satisfy_low_to_high_diff(l1, h2):
                            for l2_i_i in range(l1_i_i, len(bottom_index_list)):
                                l2_i = peak_index_list[l2_i_i]
                                l2 = x[l2_i]
                                if self._satisfy_high_to_low_diff(h2, l2):
                                    res.append(W(
                                        h1,
                                        index_to_timestamp(h1_i),
                                        h2,
                                        index_to_timestamp(h2_i),
                                        l1,
                                        index_to_timestamp(l1_i),
                                        l2,
                                        index_to_timestamp(l2_i)))
        return res

    def indicator_update_handler(self, new_indicator: np.float64, indicator_list: List[np.float64]):
        pass

    @property
    def name(self):
        return "WPattern"

    def _satisfy_low_to_high_diff(self, low: np.float64, high: np.float64) -> bool:
        return (high - low) / low > self.low_high_diff_threshold_percentage

    def _satisfy_high_to_low_diff(self, high: np.float64, low: np.float64) -> bool:
        return self._satisfy_low_to_high_diff(low, high)