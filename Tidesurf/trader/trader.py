import os
from abc import ABC
from datetime import timedelta, date
from typing import List

import pandas as pd

from Tidesurf.analytics.indicator.indicator import Indicator
from Tidesurf.config.trader.trader_config import TraderConfig


class Trader(ABC):
    symbol: str
    historic_data_dir: str
    num_day_historic_data_preload: int
    indicator_list: List[Indicator]

    def __init__(self, config: TraderConfig, indicator_list: List[Indicator]):
        self.symbol = config.symbol
        self.historic_data_dir = config.historic_data_dir
        self.num_day_historic_data_preload = config.num_day_historic_data_preload
        self.indicator_list = indicator_list

    def load_history(self):
        # load historic position data from the directory
        date_delta = timedelta(days=1)
        today = date.today()
        start_date = today - timedelta(days=self.num_day_historic_data_preload)
        cur_date = start_date
        while cur_date != today:
            data_path = self._get_symbol_historic_data_dir(
                self.symbol,
                cur_date.year,
                cur_date.month,
                cur_date.day)
            # If history for this date does not exist
            if os.path.exists(data_path):
                df = self._get_symbol_historic_data(
                    self.symbol,
                    cur_date.year,
                    cur_date.month,
                    cur_date.day)
                for row in df.iterrows():
                    for indicator in self.indicator_list:
                        indicator.append_record(row)
            cur_date += date_delta

    def _get_symbol_historic_data(self, symbol: str, year: str or int, month: str or int,
                                  day: str or int) -> pd.DataFrame:
        file_path = self._get_symbol_historic_data_dir(symbol, year, month, day)
        return pd.read_parquet(file_path)

    def _get_symbol_historic_data_dir(self, symbol: str, year: str or int, month: str or int, day: str or int) -> str:
        return os.path.join(self.historic_data_dir, symbol, str(year), str(month), f"{day}.parquet")
