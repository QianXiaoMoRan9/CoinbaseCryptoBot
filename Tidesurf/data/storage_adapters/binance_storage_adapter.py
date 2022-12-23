from Tidesurf.data.storage_adapters.storage_adapter import StorageAdapter
from Tidesurf.data.schema.binance_raw_data_columns import BinanceRawDataColumn
from typing import Tuple, Hashable, List
import pandas as pd
import numpy as np


class BinanceStorageAdapter(StorageAdapter):

    @staticmethod
    def get_timestamp(row: Tuple[Hashable, pd.Series]) -> List[int]:
        return [row[BinanceRawDataColumn.TIMESTAMP]]

    @staticmethod
    def get_price(row: Tuple[Hashable, pd.Series]) -> List[np.float64]:
        return [np.float64(row[BinanceRawDataColumn.PRICE])]

    @staticmethod
    def get_volume(row: Tuple[Hashable, pd.Series]) -> List[np.float64]:
        return [np.float64(row[BinanceRawDataColumn.VOLUME])]
