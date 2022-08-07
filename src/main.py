import os
from data.executor.execute_get_monthly_data import execute_get_monthly_data_for_product

from utils.directory_utils import get_monthly_partition_file_name
if __name__ == "__main__":
    # BASE_DIR = "./raw"
    # execute_get_monthly_data_for_product("SOL-USD", BASE_DIR)

    raw_data_dir = "./raw"
    output_data_dir = "./processed"
    product_id = "ETH-USD"
    start_year = 2019
    start_month = 1
    end_year = 2022
    end_month = 7

    for cur_year in range(start_year, end_year + 1):
        month_list = [x for x in range(1, 12 + 1)]
        if cur_year == start_year:
            month_list = [x for x in range(start_month, 12 + 1)]
        elif cur_year == end_year:
            month_list = [x for x in range(1, end_month + 1)]
        
        for cur_month in month_list:
            raw_data_path = get_monthly_partition_file_name(raw_data_dir, product_id, cur_year, cur_month)
            

