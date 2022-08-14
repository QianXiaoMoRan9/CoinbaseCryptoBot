from data.getter.get_month_candle import load_from_parquet
from datetime import datetime, timedelta
from utils.directory_utils import get_monthly_partition_file_name
from utils.datetime_utils import get_sorted_year_month
from data.model.partition import Partition
from utils.number_utils import get_interval_steps, round_float, precision_to_precision_value
"""
Assumes the directory structure is the following:
base_directory/
    product_id/
        {product_id}_{year}_{month}.paquet

start_datetime: datetime.datetime
end_datetime: datetime.datetime

"""
def get_interval_positions(base_directory: str, product_id: str, start_timestamp: int, end_timestamp: int, precision=2):
    assert start_timestamp <= end_timestamp, f"End time should be same or later then start time, got start {start_timestamp}, end {end_timestamp}"
    start_datetime = datetime.fromtimestamp(start_timestamp)
    end_datetime = datetime.fromtimestamp(end_timestamp)

    # price -> volume
    price_volume_dict = dict()
    increment = precision_to_precision_value(precision)

    for year, month in get_sorted_year_month(start_datetime, end_datetime):
        df = load_from_parquet(product_id, year, month, base_directory)
        num_record = df.shape[0]
        # calculate the interval of this df to be calculated
        df_end_timestamp = int(df[Partition.TIME][num_record - 1])
        df_start_timestamp = int(df[Partition.TIME][0])
        calculated_start_timestamp = max(df_start_index, df_start_timestamp)
        calculated_end_timestamp = min(df_end_timestamp, end_timestamp)
        # calculate the index start and index end for the calculation
        df_start_index = calculated_start_timestamp - df_start_timestamp
        df_end_index = calculated_end_timestamp - df_start_timestamp

        for df_index in range(df_start_index, df_end_index + 1):
            
            num_start = round_float(df[Partition.LOW][df_index])
            num_end = round_float(df[Partition.HIGH][df_index])
            steps = get_interval_steps(num_start, num_end, precision)
            vol = df[Partition.VOLUME] / steps
            num_val = num_start
            while num_val <= num_end:
                price_volume_dict[num_val] = price_volume_dict.get(num_val, 0.0) + vol
                num_val = round_float(num_val + increment)
    
    result_pair = price_volume_dict.items()
    result_pair.sort(key = lambda x: x[0])
    return result_pair
