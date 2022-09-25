import os
from Tidesurf.data.executor.execute_get_monthly_data import execute_get_monthly_data_for_product
from Tidesurf.data.post_processing.data_cleanup import raw_data_cleanup, verify_cleanup
# from server.websocket_feed import start_job
from Tidesurf.analytics.positions import get_interval_market_positions
from pprint import pprint

if __name__ == "__main__":
    # execute_get_monthly_data_for_product("SOL-USD", "./raw")
    # raw_data_cleanup('./raw', './processed', 'ETH-USD', 2019, 1, 2022, 7)
    # verify_cleanup('./processed', 'ETH-USD', 2018, 12, 2022, 7)

    # start_job()
    pprint(get_interval_market_positions('./processed', 'ETH-USD', 1548978840, 1580509200))

