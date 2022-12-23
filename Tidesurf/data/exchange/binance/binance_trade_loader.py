from typing import List, Tuple
from random import choice
from datetime import datetime, timedelta
import pandas as pd
import os
import numpy as np
import logging
from Tidesurf.data.exchange.binance.binance_utils import BinanceUtils
from Tidesurf.data.exchange.base_fetcher import BaseFetcher
from Tidesurf.data.schema.binance_raw_data_columns import BinanceRawDataColumn
from Tidesurf.utils.datetime_utils import from_timestamp

class BinanceTradeGenerativeLoader:
    data_dir: str
    symbol: str
    # in milliseconds
    start_timestamp: int

    timedelta: timedelta = timedelta(days=1)
    cur_datetime: datetime
    cur_df: pd.DataFrame
    cur_df_index: int
    cur_df_index: int

    exhausted = False

    def __init__(self, data_dir_list: List[str], symbol: str, start_timestamp: int):
        self.data_dir = choice(data_dir_list)
        self.symbol = symbol
        self.start_timestamp = start_timestamp

        self.cur_datetime = from_timestamp(start_timestamp)
        # load first df for the starting position
        if self._has_df_to_load():
            self._load_df_for_cur_datetime()
        else:
            self._set_exhausted()
            logging.info(f"Received timestamp that is too new to have record: {self.start_timestamp}")
            return
        # find the index for the next entry that best suits the record
        self.cur_df_index = 0
        df_timestamp = int(self.df.iloc[self.cur_df_index][BinanceRawDataColumn.TIMESTAMP])
        while df_timestamp < self.start_timestamp:
            self.cur_df_index += 1
            if self._is_cur_df_exhausted():
                self._step_date()
                if not self._has_df_to_load():
                    self._set_exhausted()
                    break
                self._load_df_for_cur_datetime()

            df_timestamp = int(self.df.iloc[self.cur_df_index][BinanceRawDataColumn.TIMESTAMP])

    def has_next(self) -> bool:
        if self.exhausted:
            return False
        if not self._is_cur_df_exhausted():
            return True
        self._step_date()
        if self._has_df_to_load():
            self._load_df_for_cur_datetime()
            return True
        return False

    # agg_id, timestamp, price, volume
    def next(self) -> Tuple[int, int, np.float64, np.float64]:
        entry = self.df.iloc[self.cur_df_index]
        result = (
            int(entry[BinanceRawDataColumn.AGG_ID]),
            int(entry[BinanceRawDataColumn.TIMESTAMP]),
            np.float64(entry[BinanceRawDataColumn.PRICE]),
            np.float64(entry[BinanceRawDataColumn.VOLUME])
        )
        self.cur_df_index += 1
        return result

    def _set_exhausted(self):
        self.exhausted = True

    def _is_cur_df_exhausted(self):
        return self.cur_df_index >= self.df.shape[0]

    def _step_date(self):
        self.cur_datetime += self.timedelta

    def _has_df_to_load(self):
        df_path = BinanceUtils.get_historic_data_path(
            self.data_dir,
            self.symbol,
            self.cur_datetime.year,
            self.cur_datetime.month,
            self.cur_datetime.day)
        return os.path.exists(df_path)

    def _load_df_for_cur_datetime(self):
        df_path = BinanceUtils.get_historic_data_path(
            self.data_dir,
            self.symbol,
            self.cur_datetime.year,
            self.cur_datetime.month,
            self.cur_datetime.day)
        self.df = BaseFetcher.load_df_from_parquet(df_path)
        self.cur_df_index = 0
