from abc import ABC, abstractmethod
from typing import Tuple, Hashable, List
import pandas as pd
import numpy as np


class StorageAdapter(ABC):

    @staticmethod
    @abstractmethod
    def get_timestamp(row: Tuple[Hashable, pd.Series]) -> List[int]:
        pass

    @staticmethod
    @abstractmethod
    def get_price(row: Tuple[Hashable, pd.Series]) -> List[np.float64]:
        pass

    @staticmethod
    @abstractmethod
    def get_volume(row: Tuple[Hashable, pd.Series]) -> List[np.float64]:
        pass
