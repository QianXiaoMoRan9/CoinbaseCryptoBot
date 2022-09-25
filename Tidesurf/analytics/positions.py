from Tidesurf.data.getter.get_month_candle import load_from_parquet
from datetime import datetime, timedelta
from Tidesurf.data.model.decimal import Decimal
from Tidesurf.utils.datetime_utils import get_sorted_year_month
from Tidesurf.data.model.partition import Partition
from Tidesurf.data.model.market_positions import MarketPositions
import numpy as np

"""
Assumes the directory structure is the following:
base_directory/
    product_id/
        {product_id}_{year}_{month}.paquet

start_datetime: datetime.datetime
end_datetime: datetime.datetime

Returns:
[
    [20.56, 500],
    [20.57, 200],
    [20.58, 100],
    ...
]
"""


def get_interval_market_positions(base_directory: str, product_id: str, start_timestamp: int, end_timestamp: int,
                                  precision=2) -> MarketPositions:
    assert start_timestamp <= end_timestamp, f"End time should be same or later then start time, got start {start_timestamp}, end {end_timestamp} "
    start_datetime = datetime.fromtimestamp(start_timestamp)
    end_datetime = datetime.fromtimestamp(end_timestamp)

    # price -> volume
    price_volume_dict: dict[Decimal, float] = dict()
    increment = Decimal.from_value(1, precision)

    for year, month in get_sorted_year_month(start_datetime, end_datetime):
        print(year, month)
        df = load_from_parquet(product_id, year, month, base_directory)
        num_record = df.shape[0]
        # calculate the interval of this df to be calculated
        df_end_timestamp = int(df[Partition.TIME][num_record - 1])
        df_start_timestamp = int(df[Partition.TIME][0])
        calculated_start_timestamp = max(start_timestamp, df_start_timestamp)
        calculated_end_timestamp = min(df_end_timestamp, end_timestamp)
        # calculate the index start and index end for the calculation
        df_start_index = (calculated_start_timestamp - df_start_timestamp) // 100
        df_end_index = (calculated_end_timestamp - df_start_timestamp) // 100
        print(df_start_index, df_end_index)

        for df_index in range(df_start_index, df_end_index + 1):
            num_start = Decimal(df[Partition.LOW][df_index], precision)
            num_end = Decimal(df[Partition.HIGH][df_index], precision)
            # print("start, end ", num_start, num_end)
            steps = num_end.value - num_start.value + 1
            # print(steps)
            vol = df[Partition.VOLUME][df_index] / steps
            num_val = num_start
            while num_val <= num_end:
                price_volume_dict[num_val] = price_volume_dict.get(num_val, 0.0) + vol
                num_val = num_val + increment
    # fill remaining gaps prices with 0
    all_prices = price_volume_dict.keys()
    min_price = min(all_prices)
    max_price = max(all_prices)
    print(min_price, max_price)
    cur_price = min_price
    while cur_price < max_price:
        if cur_price not in price_volume_dict:
            price_volume_dict[cur_price] = 0.0
        cur_price += increment

    result_pair = [[key.to_float(), val] for (key, val) in price_volume_dict.items()]
    result_pair.sort(key=lambda x: x[0])
    result_array = np.array(result_pair)
    market_position = MarketPositions(start_timestamp, end_timestamp, precision, result_array[:, 0], result_array[:, 1])
    return market_position
