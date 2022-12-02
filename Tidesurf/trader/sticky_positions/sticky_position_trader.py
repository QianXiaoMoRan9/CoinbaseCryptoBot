import os
import numpy as np
from typing import List, Dict
import pandas as pd
from datetime import date, timedelta
from Tidesurf.trader.sticky_positions.symbol_position import SymbolPosition
from Tidesurf.trader.sticky_positions.sticky_position_trader_config import StickyPositionTraderConfig
from Tidesurf.data.schema.binance_raw_data_columns import BinanceRawDataColumn
"""
Configurations
historic_data_dir: top level data directory of historic trades
num_day_historic_data_preload: number of days to preload historic data

[{
    symbol: symbol of trading product
    decay_period_sec: period interval to batch the trades together to perform a round of decay
    decay_factor: the factor for the positions to decay per period
    precision: precision in form of string such as "0.01"
}]


TODO:
1. refactor the APIs from binance specific to generic
"""


class StickyPositionTrader(object):
    historic_data_dir: str
    num_day_historic_data_preload: int

    trading_symbols: List[str]
    position_map: Dict[str, SymbolPosition]

    def __init__(self, config: StickyPositionTraderConfig):
        self.historic_data_dir = config.historic_data_dir
        self.num_day_historic_data_preload = config.num_day_historic_data_preload
        self.trading_symbols = list()

        for symbol_position_config in config.symbol_position_config_list:
            self.trading_symbols.append(symbol_position_config.symbol)
            self.position_map[symbol_position_config.symbol] = SymbolPosition(symbol_position_config)

        self._load_history()

    def _load_history(self):
        # load historic position data from the directory
        date_delta = timedelta(days=1)
        today = date.today()
        start_date = today - timedelta(days=self.num_day_historic_data_preload)
        for symbol in self.trading_symbols:
            cur_date = start_date
            symbol_position = self.position_map[symbol]
            while cur_date != today:
                data_path = self._get_symbol_historic_data_dir(symbol, cur_date.year, cur_date.month, cur_date.day)
                # If history for this date does not exist
                if not os.path.exists(data_path):
                    break
                df = self._get_symbol_historic_data(symbol, cur_date.year, cur_date.month, cur_date.day)
                for row in df.iterrows():
                    symbol_position.add_trade([
                        int(row[BinanceRawDataColumn.TIMESTAMP]),
                        np.float64(row[BinanceRawDataColumn.PRICE]),
                        np.float64(row[BinanceRawDataColumn.VOLUME])])
                cur_date += date_delta

    def _get_symbol_historic_data(self, symbol: str, year: str or int, month: str or int,
                                  day: str or int) -> pd.DataFrame:
        file_path = self._get_symbol_historic_data_dir(symbol, year, month, day)
        return pd.read_parquet(file_path)

    def _get_symbol_historic_data_dir(self, symbol: str, year: str or int, month: str or int, day: str or int) -> str:
        return os.path.join(self.historic_data_dir, symbol, str(year), str(month), f"{day}.parquet")


