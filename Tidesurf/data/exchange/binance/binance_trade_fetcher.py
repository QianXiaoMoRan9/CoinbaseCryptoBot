import requests
import os
import pandas as pd
from typing import Dict, List, Tuple
from Tidesurf.data.exchange.base_fetcher import BaseFetcher
from Tidesurf.data.schema.binance_raw_data_columns import BinanceRawDataColumn
from Tidesurf.data.exchange.binance.binance_utils import BinanceUtils
from Tidesurf.data.optimized.fast_append_data_frame import FastAppendDataFrame
from Tidesurf.utils.datetime_utils import from_timestamp

"""
output_dir/
    [symbol]/
        [year]/
            [month]/
                    [day].parquet

Schema
[
    agg_id, timestamp, price, volume
]
"""


class BinanceTradeFetcher(BaseFetcher):
    api_key: str
    output_dir: str

    def __init__(self, api_key: str, output_dir: str):
        super().__init__()
        self.api_key = api_key
        self.output_dir = output_dir

    def fetch_all_historical_trades_for_product(self,
                                                symbol: str,
                                                output_dir_list: List[str],
                                                limit: int = 1000):

        start_agg_id = 0
        cur_timestamp = 0
        # Check if the current output directory has old data before
        # If there is old data then start off where last time left off
        oldest_agg_id, df = self.get_most_recent_historical_agg_id(output_dir_list, symbol)
        if oldest_agg_id is not None:
            # step 1 to avoid overlap
            start_agg_id = int(oldest_agg_id) + 1
            print("Got start agg id: ", start_agg_id)
            cur_timestamp = int(df.iloc[-1][BinanceRawDataColumn.TIMESTAMP])
            df = FastAppendDataFrame(BinanceRawDataColumn.columns, prev_df=df)
        else:
            df = FastAppendDataFrame(columns=BinanceRawDataColumn.columns)
            # Get the starting timestamp for trade 0
            start_response = self.fetch_historical_trades_for_product(symbol, start_agg_id, limit=limit)
            cur_timestamp = start_response[0]['T']

        cur_datetime = from_timestamp(cur_timestamp)
        cur_year = cur_datetime.year
        cur_month = cur_datetime.month
        cur_day = cur_datetime.day
        print(f"Starting from datetime {cur_datetime}")
        # Get remote latest agg_id
        latest_response = self.fetch_historical_trades_for_product(symbol, None, limit=limit)
        last_agg_id = latest_response[-1]['a']
        cur_agg_id = start_agg_id
        while cur_agg_id < last_agg_id:
            response = self.fetch_historical_trades_for_product(symbol, cur_agg_id, limit=limit)
            print("Cur start agg id: ", cur_agg_id)
            for i in range(len(response)):
                row = response[i]
                row_datetime = from_timestamp(row['T'])
                if row_datetime.year != cur_year or row_datetime.month != cur_month or row_datetime.day != cur_day:
                    # save previous day's record
                    result_df = df.get_df(True)
                    print(f"Saving record for {cur_year}-{cur_month}-{cur_day}, num records: {result_df.shape[0]}")
                    self._save_to_output_dirs(output_dir_list, symbol, result_df, cur_year, cur_month, cur_day)
                    # reset parameters
                    df = FastAppendDataFrame(columns=BinanceRawDataColumn.columns)
                    cur_year = row_datetime.year
                    cur_month = row_datetime.month
                    cur_day = row_datetime.day
                df.append([row['a'], row['T'], row['p'], row['q']])
                cur_agg_id = row['a']
            cur_agg_id += 1
        result_df = df.get_df(True)
        print(f"Saving residual record for {cur_year}-{cur_month}-{cur_day}, num records: {result_df.shape[0]}")
        # save spillover
        self._save_to_output_dirs(output_dir_list, symbol, result_df, cur_year, cur_month, cur_day)

    def _save_to_output_dirs(
            self,
            output_dir_list: List[str],
            symbol: str,
            df: pd.DataFrame,
            cur_year: int,
            cur_month: int,
            cur_day: int):
        if df.shape[0]:
            for output_dir in output_dir_list:
                os.makedirs(BinanceUtils.get_historic_data_folder(output_dir, symbol, cur_year, cur_month),
                            exist_ok=True)
                self.save_df_to_parquet(
                    df,
                    BinanceUtils.get_historic_data_path(output_dir, symbol, cur_year, cur_month, cur_day))

    ######## Output folder structure ############
    @staticmethod
    def get_most_recent_historical_agg_id(output_path_list: List[str], symbol: str) \
            -> Tuple[int or None, pd.DataFrame or None]:
        """
            return None, None if does not exists
            else:
                return latest_agg_id, df
        """
        output_path = output_path_list[0]

        symbol_dir = os.path.join(output_path, symbol)
        if not os.path.exists(symbol_dir):
            return None, None

        # Get most recent year, month, day
        years = os.listdir(os.path.join(output_path, symbol))
        most_recent_year = max([int(y) for y in years])
        months = os.listdir(os.path.join(output_path, symbol, str(most_recent_year)))
        most_recent_month = max([int(m) for m in months])
        day_files = os.listdir(os.path.join(output_path, symbol, str(most_recent_year), str(most_recent_month)))
        most_recent_day = max([int(f[:f.find(".parquet")]) for f in day_files])
        most_recent_file_path = os.path.join(
            output_path, symbol,
            str(most_recent_year),
            str(most_recent_month),
            f"{most_recent_day}.parquet")
        print("Obtained most recent file path: ", most_recent_file_path)
        df = BinanceTradeFetcher.load_df_from_parquet(most_recent_file_path)
        return df.iloc[-1][BinanceRawDataColumn.AGG_ID], df

    ######## End output folder structure ############

    def fetch_historical_trades_for_product(self, symbol: str, from_id: int or None, limit: int = 1000) -> List[Dict]:
        headers = {
            'X-MBX-APIKEY': self.api_key
        }
        if from_id is None:
            resp = requests.get(f'https://api.binance.us/api/v3/aggTrades?symbol={symbol}&limit={limit}')
        else:
            resp = requests.get(
                f'https://api.binance.us/api/v3/aggTrades?symbol={symbol}&fromId={from_id}&limit={limit}')
        return resp.json()
