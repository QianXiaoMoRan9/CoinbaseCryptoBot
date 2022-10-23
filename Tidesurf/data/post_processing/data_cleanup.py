# Deduplicate data with the same timestamp
# Calibrate the data for the correct data for the correct month for each partition
import os
from tqdm import tqdm
from Tidesurf.utils.directory_utils import get_monthly_partition_file_name
from Tidesurf.data.fetcher.coinbase.get_month_candle import load_from_parquet, save_as_parquet
from datetime import datetime, timedelta, date
from Tidesurf.data.model.partition import Partition


def raw_data_cleanup(raw_data_dir, output_data_dir, symbol, start_year, start_month, end_year, end_month):
    # use sliding window to gradually shift data
    prev_year = None
    prev_month = None
    prev_data = list()

    cur_data = list()

    next_year = None
    next_month = None
    next_data = list()

    product_output_folder = os.path.join(output_data_dir, symbol)
    os.mkdir(product_output_folder) if not os.path.exists(product_output_folder) else print()

    for cur_year in range(start_year, end_year + 1):
        month_list = [x for x in range(1, 12 + 1)]
        if cur_year == start_year:
            month_list = [x for x in range(start_month, 12 + 1)]
        elif cur_year == end_year:
            month_list = [x for x in range(1, end_month + 1)]

        for cur_month in month_list:
            raw_data_df = load_from_parquet(symbol, cur_year, cur_month, raw_data_dir)

            for _, row in raw_data_df.iterrows():
                cur_time = datetime.fromtimestamp(row[Partition.TIME])
                if cur_time.year < cur_year or cur_time.month < cur_month:

                    if prev_year is None:
                        prev_year = cur_time.year
                        prev_month = cur_time.month
                    else:
                        if (prev_year != cur_time.year) or (prev_month != cur_time.month):
                            raise Exception(
                                f"We should not get multiple prev year month. prev: {prev_year}/{prev_month}, cur_time: {cur_time.year}/{cur_time.month}")

                    dedup_result = dedup_and_pad_from_tail(prev_data, partition_row_to_list(row))
                    if dedup_result:
                        prev_data.extend(dedup_result)
                elif cur_time.year > cur_year or cur_time.month > cur_month:
                    if next_year is None:
                        next_year = cur_time.year
                        next_month = cur_time.month
                    else:
                        if (next_year != cur_time.year) or (next_month != cur_time.month):
                            raise Exception(
                                f"We should not get multiple prev year month. prev: {next_year}/{next_month}, cur_time: {cur_time.year}/{cur_time.month}")
                    dedup_result = dedup_and_pad_from_tail(next_data, partition_row_to_list(row))
                    if dedup_result:
                        next_data.extend(dedup_result)
                else:
                    assert cur_year == cur_time.year and cur_month == cur_time.month, "Expect time match cur: {cur_year}/{cur_month}, cur_time: {cur_time.year}/{cur_time.month}"
                    dedup_result = dedup_and_pad_from_tail(cur_data, partition_row_to_list(row))
                    if dedup_result:
                        cur_data.extend(dedup_result)
            # save prev, reset prev
            prev_data.extend(get_padded_list_backward(prev_data))
            consolidate_save_as_parquet(prev_data, symbol, prev_year, prev_month, output_data_dir)
            prev_month = cur_month
            prev_year = cur_year
            prev_data = cur_data
            # next becomes cur, reset next
            cur_data = next_data
            next_year = None
            next_month = None
            next_data = list()
            print(prev_year, prev_month, cur_year, cur_month, next_year, next_month)
    prev_data.extend(get_padded_list_backward(prev_data))
    consolidate_save_as_parquet(prev_data, symbol, prev_year, prev_month, output_data_dir)
    print(f"Saving final remaining: {prev_year}/{prev_month}")
    if (cur_data):
        cur_time = datetime.fromtimestamp(cur_data[0][0])
        cur_data.extend(get_padded_list_backward(cur_data))
        consolidate_save_as_parquet(cur_data, symbol, cur_time.year, cur_time.month, output_data_dir)
        print(f"Saving next month spillover: {cur_time.year}/{cur_time.month}")


def verify_cleanup(data_dir, symbol, start_year, start_month, end_year, end_month):
    for cur_year in range(start_year, end_year + 1):
        month_list = [x for x in range(1, 12 + 1)]
        if cur_year == start_year:
            month_list = [x for x in range(start_month, 12 + 1)]
        elif cur_year == end_year:
            month_list = [x for x in range(1, end_month + 1)]

        for cur_month in month_list:
            verify_product_month_data(symbol, cur_year, cur_month, data_dir)
            print(f"Finished verifying {cur_year}/{cur_month}")


def verify_product_month_data(symbol, year, month, output_folder):
    df = load_from_parquet(symbol, year, month, output_folder)
    cur_time = 0
    start_time = 0
    end_time = 0
    for _, row in tqdm(df.iterrows()):
        if cur_time == 0:
            cur_time = row[Partition.TIME]
            start_time = cur_time
            continue
        now = row[Partition.TIME]
        if int(now) - cur_time != 60:
            print(
                f"Problem, non increading sequence now: {datetime.fromtimestamp(now)}, cur_time: {datetime.fromtimestamp(cur_time)}")
        cur_time = int(now)
    end_time = cur_time
    start_time_object = datetime.fromtimestamp(start_time)
    end_time_object = datetime.fromtimestamp(end_time)
    if (start_time_object.year != year or start_time_object.month != month):
        print(
            f"Start time does not align with the input, expected y:m {year}:{month}, got {start_time_object.year}:{start_time_object.month}")
    if (start_time_object.hour != 0 or start_time_object.minute != 0 or start_time_object.second != 0):
        print(f"Start time is not zero o clock")
    if (end_time_object.year != year or end_time_object.month != month):
        print(
            f"End time does not align with the input, expected y:m {year}:{month}, got {end_time_object.year}:{end_time_object.month}")
    if (end_time_object.hour != 23 or end_time_object.minute != 59 or end_time_object.second != 0):
        print(f"Start time is not last second")


def partition_row_to_list(row):
    return [
        row[Partition.TIME],
        row[Partition.LOW],
        row[Partition.HIGH],
        row[Partition.OPEN],
        row[Partition.CLOSE],
        row[Partition.VOLUME],
    ]


def dedup_and_pad_from_tail(existing_data_list, new_row):
    pad_start_timestamp = 0
    new_row_time = datetime.fromtimestamp(new_row[0])
    if len(existing_data_list) == 0:
        pad_start_timestamp = datetime(new_row_time.year, new_row_time.month, 1, 0, 0, 0).timestamp()
        return get_padded_list_forward(pad_start_timestamp, new_row)
    last_timestamp = existing_data_list[-1][0]
    last_time = datetime.fromtimestamp(last_timestamp)
    if last_time >= new_row_time:
        return []
    return get_padded_list_forward(last_timestamp + 60, new_row)


def get_padded_list_forward(start_timestamp, cur_row):
    start_timestamp = int(start_timestamp)
    cur_timestamp = int(cur_row[0])
    result = [
        [i_timestamp, 0, 0, 0, 0, 0] for i_timestamp in range(start_timestamp, cur_timestamp, 60)
    ]
    result.append(cur_row)
    return result


def get_padded_list_backward(existing_data_list):
    tail_timestamp = int(existing_data_list[-1][0])
    end_timestamp = int(get_last_day_of_month_timestap(tail_timestamp))
    return [
        [i_timestamp, 0, 0, 0, 0, 0] for i_timestamp in range(tail_timestamp + 60, end_timestamp + 60, 60)
    ]


def get_last_day_of_month_timestap(timestamp):
    # returns the timestamp oft he last second of the month for the month that input timestamp is in
    dt = datetime.fromtimestamp(timestamp)
    last_date = last_day_of_month(date(dt.year, dt.month, dt.day))
    return datetime(last_date.year, last_date.month, last_date.day, 23, 59, 0).timestamp()


def last_day_of_month(any_day):
    # The day 28 exists in every month. 4 days later, it's always next month
    next_month = any_day.replace(day=28) + timedelta(days=4)
    # subtracting the number of the current day brings us back one month
    return next_month - timedelta(days=next_month.day)


def consolidate_save_as_parquet(data_array, symbol, year, month, output_data_dir):
    # Load existing data partition of the month, if exists
    existing_partition_name = get_monthly_partition_file_name(output_data_dir, symbol, year, month)
    if not os.path.exists(existing_partition_name):
        save_as_parquet(data_array, symbol, year, month, output_data_dir)
        return
    existing_partition_df = load_from_parquet(symbol, year, month, output_data_dir)
    assert int(data_array[0][0]) == int(existing_partition_df[Partition.TIME][0]), "Start time does not align"
    assert int(data_array[-1][0]) == int(
        existing_partition_df[Partition.TIME][existing_partition_df.shape[0] - 1]), "End timestamp does not align"

    for i in range(len(data_array)):
        if int(existing_partition_df[Partition.VOLUME][i]) != 0 and data_array[i][5] == 0:
            assert int(data_array[i][0]) == int(existing_partition_df[Partition.VOLUME][i]), "Timestamp does not match"
            data_array[i][1] = existing_partition_df[Partition.LOW][i]
            data_array[i][2] = existing_partition_df[Partition.HIGH][i]
            data_array[i][3] = existing_partition_df[Partition.OPEN][i]
            data_array[i][4] = existing_partition_df[Partition.CLOSE][i]
            data_array[i][5] = existing_partition_df[Partition.VOLUME][i]
    save_as_parquet(data_array, symbol, year, month, output_data_dir)
