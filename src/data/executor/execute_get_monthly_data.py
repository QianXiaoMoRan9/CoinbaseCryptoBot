import os

from data.getter.get_month_candle import get_and_save_product_month_data, verify_product_month_data
from data.getter.get_product_list import get_product_list

def execute_get_monthly_data_for_all_product(raw_data_dir):
    product_list = get_product_list()
    for product_id in product_list:
        execute_get_monthly_data_for_product(product_id, raw_data_dir)

def execute_get_monthly_data_for_product(product_id, raw_data_dir):
    product_dir = os.path.join(raw_data_dir, product_id)
    os.mkdir(product_dir) if not os.path.exists(product_dir) else print("")
    for year in [2019, 2020, 2021, 2022]:
        month_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 ,12]
        if year == 2022:
            month_list = [1, 2, 3, 4, 5, 6, 7]
        for month in month_list:
            print(f"Starting year/month: {year}/{month}")
            get_and_save_product_month_data(product_id, year, month, product_dir)