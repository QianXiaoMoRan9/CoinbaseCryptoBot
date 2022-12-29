from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Iterable, Callable
from Tidesurf.analytics.indicator.indicator import INDICATOR_TYPE
from Tidesurf.trader.trader import Trader

PATTERN_INDICATOR_TYPE = TypeVar("PATTERN_INDICATOR_TYPE")
PATTERN_TYPE = TypeVar("PATTERN_TYPE")


class Algorithm(ABC, Generic[PATTERN_INDICATOR_TYPE, PATTERN_TYPE, INDICATOR_TYPE]):

    trader: Trader

    def __init__(self, trader: Trader):
        self.trader = trader

    @abstractmethod
    def get_all_candidates(
            self,
            x: Iterable[PATTERN_INDICATOR_TYPE],
            index_to_timestamp: Callable[[int], int]) -> List[PATTERN_TYPE]:
        pass

    @abstractmethod
    def indicator_update_handler(self, new_indicator: INDICATOR_TYPE, indicator_list: List[INDICATOR_TYPE]):
        pass

    @abstractmethod
    @property
    def name(self):
        pass
