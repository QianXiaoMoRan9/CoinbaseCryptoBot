import os
from abc import ABC, abstractmethod
from datetime import timedelta, date
from typing import List, Generic

import pandas as pd
from Tidesurf.analytics.algorithms.algorithm import Algorithm
from Tidesurf.analytics.indicator.indicator import Indicator, INDICATOR_TYPE
from Tidesurf.config.trader.trader_config import TraderConfig
from Tidesurf.exchange_adapter.exchange_adapter import ExchangeAdapter
from Tidesurf.position_manager.position_manager import PositionManager
import numpy as np


class Trader(ABC, Generic[INDICATOR_TYPE]):
    symbol: str
    trade_mode: str
    historic_data_dir: str
    num_day_historic_data_preload: int
    instrument_allow_partial: bool
    indicator: Indicator
    algorithm: Algorithm
    position_manager: PositionManager
    exchange_adapter: ExchangeAdapter

    def __init__(self, config: TraderConfig, indicator: Indicator, algorithm: Algorithm,
                 position_manager: PositionManager, exchange_adapter: ExchangeAdapter):
        self.symbol = config.symbol
        self.trade_mode = config.trade_mode
        self.historic_data_dir = config.historic_data_dir
        self.num_day_historic_data_preload = config.num_day_historic_data_preload
        self.instrument_allow_partial = config.instrument_allow_partial
        self.indicator = indicator
        self.algorithm = algorithm
        self.position_manager = position_manager
        self.exchange_adapter = exchange_adapter

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
                    self.indicator.append_record(row)
            cur_date += date_delta

    def _get_symbol_historic_data(self, symbol: str, year: str or int, month: str or int,
                                  day: str or int) -> pd.DataFrame:
        file_path = self._get_symbol_historic_data_dir(symbol, year, month, day)
        return pd.read_parquet(file_path)

    def _get_symbol_historic_data_dir(self, symbol: str, year: str or int, month: str or int, day: str or int) -> str:
        return os.path.join(self.historic_data_dir, symbol, str(year), str(month), f"{day}.parquet")

    # Handlers
    def indicator_updates_handler(self, new_indicator: INDICATOR_TYPE, indicator_list: List[INDICATOR_TYPE]):
        self.algorithm.indicator_update_handler(new_indicator, indicator_list)

    def algorithm_position_entry_handler(self, price: np.float64, stop_loss: np.float64, confidence: np.float64):
        """
        Upon request of position entry from the algorithm indicating a new position entry request
        0. Fiter determine the confidence
        1. Contact the position manager to determine quantity and register the trade in the DB
        2. Contact the exchange_adapter adapter to place the order
        """
        if confidence > 0.5:
            allocated_quantity = self.position_manager.get_instrument_quantity(price, self.instrument_allow_partial)
            if self.position_manager.is_accepted_position(allocated_quantity):
                # register trade in DB
                self.position_manager.create_trade(
                    self.symbol,
                    self.exchange_adapter.exchange_name,
                    price,
                    allocated_quantity,
                    stop_loss,
                    self.algorithm.name,
                    False,
                    self.trade_mode
                )
                # Contact exchange_adapter adapter to place order
                pass
