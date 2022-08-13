import os
from data.executor.execute_get_monthly_data import execute_get_monthly_data_for_product
from data.post_processing.data_cleanup import raw_data_cleanup, verify_cleanup

if __name__ == "__main__":
    # execute_get_monthly_data_for_product("SOL-USD", "./raw")
    raw_data_cleanup('./raw', './processed', 'ETH-USD', 2019, 1, 2022, 7)
    verify_cleanup('./processed', 'ETH-USD', 2018, 12, 2022, 7)


