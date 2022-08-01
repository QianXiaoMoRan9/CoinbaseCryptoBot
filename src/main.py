from data.get_month_candle import get_and_save_product_month_data, verify_product_month_data
from data.get_product_list import get_product_list
import os
PRODUCT_LIST = get_product_list()

if __name__ == "__main__":
    BASE_DIR = "./output"
    for product_id in PRODUCT_LIST:
        print(f"Starting product: {product_id}")
        product_dir = os.path.join(BASE_DIR, product_id)
        os.mkdir(product_dir) if not os.path.exists(product_dir) else print("")
        for year in [2019, 2020, 2021, 2022]:
            month_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 ,12]
            if year == 2022:
                month_list = [1, 2, 3, 4, 5, 6]
            for month in month_list:
                print(f"Starting year/month: {year}/{month}")
                get_and_save_product_month_data(product_id, year, month, product_dir)
    # verify_product_month_data("BTC-USD", 2022, 4, "./output")