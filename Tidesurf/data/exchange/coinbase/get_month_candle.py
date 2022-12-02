import json
from unittest import result
import requests
import os
from datetime import datetime, timedelta
import pyarrow.parquet as pq
import pandas as pd
import pyarrow as pa
import time
from Tidesurf.utils.directory_utils import get_monthly_partition_file_name
from Tidesurf.data.model.partition import Partition

TPS = 3
MAX_RECORD = 300
GRANULARITY = timedelta(minutes=1)
SLEEP_TIME = 1 / (TPS - 1)

"""
Example input:
    "BTC-USD",
    2022,
    4,
    "../../output"
"""


def get_and_save_product_month_data(symbol, year, month, output_folder):
    result_array = get_product_month_candle(symbol, year, month)
    if (len(result_array) != 0) and (len(result_array[0]) != 0):
        save_as_parquet(result_array, symbol, year, month, output_folder)
    else:
        print(f"No data found for {symbol}, for {year}/{month}, not saving")


def get_product_month_candle(symbol, year, month):
    month_start = f"{year}-{fill_zero(month)}-01T00:00:00"
    delta = timedelta(minutes=MAX_RECORD)
    start_time = datetime.fromisoformat(month_start)
    start_time = start_time - GRANULARITY
    result_array = []
    while True:
        end_time = start_time + delta
        if end_time.month != start_time.month:
            end_time = find_last_minute_in_month(month, end_time)
        if start_time == end_time:
            break
        result = request_data(symbol, start_time, end_time)
        result.reverse()
        if len(result) != 0:
            result_array.extend(result)
        start_time = end_time
        if start_time.month != month:
            break
        # sleep to satisfy TPS requirement
        time.sleep(SLEEP_TIME)
    return result_array


def save_as_parquet(result_array, symbol, year, month, output_folder):
    if (result_array):
        df = pd.DataFrame(result_array)
        df.columns = Partition.COLUMNS
        table = pa.Table.from_pandas(df)
        pq.write_table(table, get_monthly_partition_file_name(output_folder, symbol, year, month))


def load_from_parquet(symbol, year, month, output_folder):
    return pd.read_parquet(get_monthly_partition_file_name(output_folder, symbol, year, month), engine='pyarrow')


def request_data(symbol, start_time, end_time):
    try:
        url = f"https://api.exchange.coinbase.com/products/{symbol}/candles?granularity={60}&start={start_time.isoformat()}&end={end_time.isoformat()}"
        headers = {"Accept": "application/json"}
        print("Before response ", symbol, start_time, end_time)
        response = requests.get(url, headers=headers)
        print("after response", response)
        return json.loads(response.text)
    except:
        print(f"Failed to request {symbol}, {start_time} - {end_time}")
        return []


def find_last_minute_in_month(month, end_time):
    delta = GRANULARITY
    while end_time.month != month:
        end_time = end_time - delta
    return end_time


def fill_zero(n):
    if (n < 10):
        return f"0{n}"
    return n


if __name__ == "__main__":
    get_and_save_product_month_data("BTC-USD", 2022, 4, "./output")
