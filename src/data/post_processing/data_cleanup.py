# Deduplicate data with the same timestamp
# Calibrate the data for the correct data for the correct month for each partition
import os
from tqdm import tqdm
from utils.directory_utils import get_monthly_partition_file_name
from data.getter.get_month_candle import load_from_parquet, save_as_parquet
from datetime import datetime
from data.model.partition import Partition

def raw_data_cleanup(raw_data_dir, output_data_dir, product_id, start_year, start_month, end_year, end_month):
    # use sliding window to gradually shift data
    prev_year = None
    prev_month = None
    prev_data = list()

    cur_data = list()

    next_year = None
    next_month = None
    next_data = list()

    product_output_folder = os.path.join(output_data_dir, product_id)
    os.mkdir(product_output_folder) if not os.path.exists(product_output_folder) else print()

    for cur_year in range(start_year, end_year + 1):
        month_list = [x for x in range(1, 12 + 1)]
        if cur_year == start_year:
            month_list = [x for x in range(start_month, 12 + 1)]
        elif cur_year == end_year:
            month_list = [x for x in range(1, end_month + 1)]
        
        for cur_month in month_list:
            raw_data_df = load_from_parquet(product_id, cur_year, cur_month, raw_data_dir)

            for _, row in raw_data_df.iterrows():
                cur_time = datetime.fromtimestamp(row[Partition.TIME])
                if cur_time.year < cur_year or cur_time.month < cur_month:

                    if prev_year is None:
                        prev_year = cur_time.year
                        prev_month = cur_time.month 
                    else:
                        if (prev_year != cur_time.year) or (prev_month != cur_time.month):
                            raise Exception(f"We should not get multiple prev year month. prev: {prev_year}/{prev_month}, cur_time: {cur_time.year}/{cur_time.month}")

                    dedup_result = dedup_from_tail(prev_data, partition_row_to_list(row))
                    if dedup_result:
                        prev_data.append(dedup_result)
                elif cur_time.year > cur_year or cur_time.month > cur_month:
                    if next_year is None:
                        next_year = cur_time.year
                        next_month = cur_time.month
                    else:
                        if (next_year != cur_time.year) or (next_month != cur_time.month):
                            raise Exception(f"We should not get multiple prev year month. prev: {next_year}/{next_month}, cur_time: {cur_time.year}/{cur_time.month}")
                    dedup_result = dedup_from_tail(next_data, partition_row_to_list(row))
                    if dedup_result:
                        next_data.append(dedup_result)
                else:
                    assert cur_year == cur_time.year and cur_month == cur_time.month, "Expect time match cur: {cur_year}/{cur_month}, cur_time: {cur_time.year}/{cur_time.month}"
                    dedup_result = dedup_from_tail(cur_data, partition_row_to_list(row))
                    if dedup_result:
                        cur_data.append(dedup_result)
            # save prev, reset prev
            save_as_parquet(prev_data, product_id, prev_year, prev_month, output_data_dir)
            prev_month = cur_month
            prev_year = cur_year
            prev_data = cur_data
            # next becomes cur, reset next
            cur_data = next_data
            next_year = None
            next_month = None
            next_data = list()
            print(prev_year, prev_month, cur_year, cur_month, next_year, next_month)
    save_as_parquet(prev_data, product_id, prev_year, prev_month, output_data_dir)
    print(f"Saving final remaining: {prev_year}/{prev_month}")
    if (cur_data):
        cur_time = datetime.fromtimestamp(cur_data[0][0])
        save_as_parquet(cur_data, product_id, cur_time.year, cur_time.month, output_data_dir)
        print(f"Saving next month spillover: {cur_time.year}/{cur_time.month}")

def verify_cleanup(data_dir, product_id, start_year, start_month, end_year, end_month):
    for cur_year in range(start_year, end_year + 1):
        month_list = [x for x in range(1, 12 + 1)]
        if cur_year == start_year:
            month_list = [x for x in range(start_month, 12 + 1)]
        elif cur_year == end_year:
            month_list = [x for x in range(1, end_month + 1)]
        
        for cur_month in month_list:
            verify_product_month_data(product_id, cur_year, cur_month, data_dir)
            print(f"Finished verifying {cur_year}/{cur_month}")

def verify_product_month_data(product_id, year, month, output_folder):
    df = load_from_parquet(product_id, year, month, output_folder)
    cur_time = 0
    start_time = 0
    end_time = 0
    for _, row in tqdm(df.iterrows()):
        if cur_time == 0:
            cur_time = row[Partition.TIME]
            start_time = cur_time
            continue
        now = row[Partition.TIME]
        if now < cur_time:
            print(f"Problem, non increading sequence now: {datetime.fromtimestamp(now)}, cur_time: {datetime.fromtimestamp(cur_time)}")
        elif now == cur_time:
            print(f"Problem, duplicating sequence now: {datetime.fromtimestamp(now)}, cur_time: {datetime.fromtimestamp(cur_time)}")
        cur_time = now
    end_time = cur_time
    start_time_object = datetime.fromtimestamp(start_time)
    end_time_object = datetime.fromtimestamp(end_time)
    if (start_time_object.year != year or start_time_object.month != month):
        print(f"Start time does not align with the input, expected y:m {year}:{month}, got {start_time_object.year}:{start_time_object.month}")
    if (end_time_object.year != year or end_time_object.month != month):
        print(f"End time does not align with the input, expected y:m {year}:{month}, got {end_time_object.year}:{end_time_object.month}")

def partition_row_to_list(row):
    return [
        row[Partition.TIME],
        row[Partition.LOW],
        row[Partition.HIGH],
        row[Partition.OPEN],
        row[Partition.CLOSE],
        row[Partition.VOLUME],
    ]

def dedup_from_tail(existing_data_list, new_row):
    if len(existing_data_list) == 0:
        return new_row
    last_time = datetime.fromtimestamp(existing_data_list[-1][0])
    row_time = datetime.fromtimestamp(new_row[0])

    if last_time >= row_time:
        return []
    
    return new_row

    