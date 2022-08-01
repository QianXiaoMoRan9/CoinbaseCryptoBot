from doctest import OutputChecker
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
SLEEP_TIME = 1/(TPS - 1)

"""
Example input:
    "BTC-USD",
    2022,
    4,
    "../../output"
"""
def get_and_save_product_month_data(product_id, year, month, output_folder):
    result_array = get_product_month_candle(product_id, year, month)
    save_as_parquet(result_array, product_id, year, month, output_folder)
    verify_product_month_data(product_id, year, month, output_folder)

def verify_product_month_data(product_id, year, month, output_folder):
    df = load_from_parquet(product_id, year, month, output_folder)
    cur_time = 0
    start_time = 0
    end_time = 0
    for _, row in df.iterrows():
        if cur_time == 0:
            cur_time = row["time"]
            start_time = cur_time
            continue
        now = row["time"]
        if now - cur_time != 60:
            print(f"Problem, now: {datetime.fromtimestamp(now)}, cur_time: {datetime.fromtimestamp(cur_time)}")
        cur_time = now
    end_time = cur_time
    start_time_object = datetime.fromtimestamp(start_time)
    end_time_object = datetime.fromtimestamp(end_time)
    if (start_time_object.year != year or start_time_object.month != month, start_time):
        print(f"Start time does not align with the input, expected y:m {year}:{month}, got {start_time_object.year}:{start_time_object.month}")
    if (start_time_object.hour != 0 or start_time_object.minute != 0):
        print(f"Start time got does not start from 0 o'cock: hour:minute {start_time_object}")
    if (end_time_object.year != year or end_time_object.month != month):
        print(f"End time does not align with the input, expected y:m {year}:{month}, got {end_time_object.year}:{end_time_object.month}")
    if (end_time_object.hour != 23 or end_time_object.minute != 59):
        print(f"Start time got does not ennd in 23:59 o'cock: hour:minute {end_time_object}")
    


def get_product_month_candle(product_id, year, month):
    month_start = f"{year}-{fill_zero(month)}-01T00:00:00"
    delta = timedelta(minutes=MAX_RECORD)
    start_time = datetime.fromisoformat(month_start)
    start_time = start_time - GRANULARITY
    result_array = []
    while True:
        end_time = start_time + delta
        if end_time.month != start_time.month:
            end_time = find_last_minute_in_month(month, end_time)
        if (start_time == end_time):
            break
        result = request_data(product_id, start_time, end_time)
        result.reverse()
        if (len(result) == 0):
            continue
        result_array.extend(result)
        start_time = end_time
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

def load_from_parquet(product_id, year, month, output_folder):
    return pd.read_parquet(f'{output_folder}/{product_id}_{year}_{month}.parquet', engine='pyarrow')

def request_data(product_id, start_time, end_time):
    try:
        url = f"https://api.exchange.coinbase.com/products/{product_id}/candles?granularity={60}&start={start_time.isoformat()}&end={end_time.isoformat()}"
        headers = {"Accept": "application/json"}
        response = requests.get(url, headers=headers)
        return json.loads(response.text)
    except:
        print(f"Failed to request {product_id}, {start_time} - {end_time}")
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