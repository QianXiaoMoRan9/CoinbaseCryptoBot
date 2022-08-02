from data.get_month_candle import load_from_parquet
from datetime import datetime, timedelta
from utils.directory_utils import get_monthly_partition_file_name
"""
Assumes the directory structure is the following:
base_directory/
    product_id/
        {product_id}_{year}_{month}.paquet

start_time: datetime.datetime
end_time: datetime.datetime

"""
def get_interval_positions(base_directory: str, product_id: str, start_time: datetime, end_time: datetime):
    assert start_time <= end_time, f"End time should be same or later then start time, got start {start_time}, end {end_time}"
    start_year = start_time.year
    end_year = end_time.year
    start_month = start_time.month
    end_month = end_time.month
    
