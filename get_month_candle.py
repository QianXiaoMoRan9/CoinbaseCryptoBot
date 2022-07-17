import json
import requests
import os
from datetime import datetime, timedelta
import pyarrow.parquet as pq
import pandas as pd
import pyarrow as pa
import time
TPS = 3
MAX_RECORD = 300
GRANULARITY = timedelta(minutes=1)
SLEEP_TIME = 1/TPS


def get_and_save_product_month_data(product_id, year, month, output_folder):
    result_array = get_product_month_candle(product_id, year, month)
    save_as_parquet(result_array, product_id, year, month, output_folder)

def get_product_month_candle(product_id, year, month):
    month_start = f"{year}-{fill_zero(month)}-01T00:00:00"
    delta = timedelta(minutes=MAX_RECORD)
    start_time = datetime.fromisoformat(month_start)
    result_array = []
    while True:
        end_time = start_time + delta
        print(start_time, end_time)
        if end_time.month != start_time.month:
            end_time = find_last_minute_in_month(month, end_time)
        result = request_data(product_id, start_time, end_time)
        result_array.extend(result)
        start_time = end_time + GRANULARITY
        if (start_time.month != month):
            break
        # sleep to satisfy TPS requirement
        time.sleep(SLEEP_TIME)
    return result_array

def save_as_parquet(result_array, product_id, year, month, output_folder):
    df = pd.DataFrame(result_array)
    df.columns=["time", "low", "high", "open", "close", "volume"]
    table = pa.Table.from_pandas(df)
    pq.write_table(table, os.path.join(output_folder, f'{product_id}_{year}_{month}.parquet'))

def request_data(product_id, start_time, end_time):
    url = f"https://api.exchange.coinbase.com/products/{product_id}/candles?granularity={60}&start={start_time.isoformat()}&end={end_time.isoformat()}"
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)
    return json.loads(response.text)

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