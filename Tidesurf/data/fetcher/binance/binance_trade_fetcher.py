import requests
import os
from datetime import date, datetime
import pandas as pd
from typing import Dict, List
from Tidesurf.data.fetcher.base_fetcher import BaseFetcher

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
                                                start_agg_id: int = 0,
                                                limit: int = 1000):
        latest_response = self.fetch_historical_trades_for_product(symbol, None, limit=limit)
        last_agg_id = latest_response[-1]['a']

        df = pd.DataFrame(columns=['agg_id', 'timestamp', 'price', 'volume'])
        cur_df_index = 0
        start_response = self.fetch_historical_trades_for_product(symbol, start_agg_id, limit=limit)
        cur_datetime = datetime.fromtimestamp(start_response[0]['T'] // 1000)
        cur_year = cur_datetime.year
        cur_month = cur_datetime.month
        cur_day = cur_datetime.day
        cur_agg_id = start_agg_id
        while cur_agg_id < last_agg_id:
            response = self.fetch_historical_trades_for_product(symbol, cur_agg_id, limit=limit)
            print("Cur start agg id: ", cur_agg_id)
            for i in range(len(response)):
                row = response[i]
                row_datetime = datetime.fromtimestamp(row['T'] // 1000)
                if row_datetime.year != cur_year or row_datetime.month != cur_month or row_datetime.day != cur_day:
                    # save previous
                    if df.shape[0]:
                        for output_dir in output_dir_list:
                            os.makedirs(self.get_historic_data_folder(output_dir, symbol, cur_year, cur_month),
                                        exist_ok=True)
                            self.save_df_to_parquet(
                                df,
                                self.get_historic_data_path(output_dir, symbol, cur_year, cur_month, cur_day))
                    # reset parameters
                    cur_df_index = 0
                    df = pd.DataFrame(columns=['agg_id', 'timestamp', 'price', 'volume'])
                    cur_year = row_datetime.year
                    cur_month = row_datetime.month
                    cur_day = row_datetime.day
                df.loc[cur_df_index] = [row['a'], row['T'] // 1000, row['p'], row['q']]
                cur_df_index += 1
                cur_agg_id = row['a']
            cur_agg_id += 1

    ######## Output folder structure ############
    @staticmethod
    def get_most_recent_historical_agg_id(output_path_list: List[str], symbol: str):
        output_path = output_path_list[0]
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
        return df.iloc[-1]['agg_id']

    @staticmethod
    def get_historic_data_folder(output_path: str, symbol: str, year: str or int, month: str or int) -> str:
        return os.path.join(output_path, output_path, symbol, str(year), str(month))

    @staticmethod
    def get_historic_data_path(output_path: str, symbol: str, year: str or int, month: str or int,
                               day: str or int) -> str:
        return os.path.join(
            BinanceTradeFetcher.get_historic_data_folder(output_path, symbol, year, month),
            f"{str(day)}.parquet")

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
