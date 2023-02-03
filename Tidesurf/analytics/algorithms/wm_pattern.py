from typing import List, Callable, Set, Tuple

import numpy as np
import numpy.typing as npt
from scipy.signal import find_peaks

from Tidesurf.analytics.algorithms.algorithm import Algorithm
from Tidesurf.analytics.algorithms.wm import W
from Tidesurf.trader.trader import Trader


class WPattern(Algorithm[np.float64, W, np.float64]):

    # minimum percentage that low and high are different w.r.t. low
    low_high_diff_threshold_percentage: np.float64
    index_to_timestamp: Callable[[int], int]
    pattern_list: List[W]
    dedup_pattern_set: Set[W]

    def __init__(self, trader: Trader, low_high_diff_threshold_percentage: np.float64, index_to_timestamp: Callable[[int], int]):
        super().__init__(trader)
        self.low_high_diff_threshold_percentage = low_high_diff_threshold_percentage
        self.index_to_timestamp = index_to_timestamp

    # 1D numpy array of an indicator sequence
    def get_all_candidates(self, x: npt.NDArray[np.float64]) -> List[W]:
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
                                        self.index_to_timestamp(h1_i),
                                        h2,
                                        self.index_to_timestamp(h2_i),
                                        l1,
                                        self.index_to_timestamp(l1_i),
                                        l2,
                                        self.index_to_timestamp(l2_i)))
        return res

    def load_history_record(self, x: npt.NDArray[np.float64]):
        self.pattern_list = self.get_all_candidates(x)

    def indicator_update_handler(self, new_indicator: np.float64, indicator_list: List[np.float64]):
        # TODO: this REALLY needs to be optimized
        """
        use new indicator:
        1.Find all triggered W pattern from record
        2. Calculate confidence score and stop loss
        3. rank the best confidence and call trader handle algorithm position entry
        4. Add all triggered to dedup set

        use indicator list:
        1. Get all candidates
        2. dedup triggered patterns
        3. put to the new pattern list
        """
        triggered_list = list()
        for pattern in self.pattern_list:
            if new_indicator >= pattern.h2:
                triggered_list.append((pattern, self.calculate_pattern_confidence(pattern)))

        triggered_list.sort(reverse=True, key=lambda x: x[1])
        for triggered_pattern in triggered_list[0]:
            self.dedup_pattern_set.add(triggered_pattern)

        candidate_list = self.get_all_candidates(np.array(indicator_list))
        new_pattern_list = list()
        for new_candidate in candidate_list:
            if new_candidate not in self.dedup_pattern_set:
                new_pattern_list.append(new_candidate)
        self.pattern_list = new_pattern_list

        selected_pattern = triggered_list[0][0]

        self.trader.algorithm_position_entry_handler(selected_pattern.h2, selected_pattern.l2, triggered_list[0][1])

    def calculate_pattern_confidence(self, pattern: W):
        return 0.5

    @property
    def name(self):
        return "WPattern"

    def _satisfy_low_to_high_diff(self, low: np.float64, high: np.float64) -> bool:
        return (high - low) / low > self.low_high_diff_threshold_percentage

    def _satisfy_high_to_low_diff(self, high: np.float64, low: np.float64) -> bool:
        return self._satisfy_low_to_high_diff(low, high)
