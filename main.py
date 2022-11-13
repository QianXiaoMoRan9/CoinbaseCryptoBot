import os
from Tidesurf.data.executor.execute_get_monthly_data import execute_get_monthly_data_for_product
from Tidesurf.data.post_processing.data_cleanup import raw_data_cleanup, verify_cleanup
# from server.websocket_feed import start_job
from Tidesurf.analytics.positions import get_interval_market_positions
from pprint import pprint
from datetime import datetime
from Tidesurf.data.fetcher.binance.binance_trade_fetcher import BinanceTradeFetcher
if __name__ == "__main__":
    # execute_get_monthly_data_for_product("SOL-USD", "./raw")
    # raw_data_cleanup('./raw', './processed', 'ETH-USD', 2019, 1, 2022, 7)
    # verify_cleanup('./processed', 'ETH-USD', 2018, 12, 2022, 7)

    # start_job()
    # pprint(get_interval_market_positions('./processed', 'ETH-USD', 1548978840, 1580509200))
    # fetcher = BinanceHistoricalTradeFetcher(os.environ.get("BINANCE_API_KEY"), "")
    # response = fetcher.fetch_historical_trades_for_product("BTCUSD", 0)
    # print(datetime.fromtimestamp(response[0]['T'] // 1000), response[0]['a'], response[0]['f'])
    # print(datetime.fromtimestamp(response[-1]['T'] // 1000), response[-1]['a'], response[-1]['f'])
    fetcher = BinanceTradeFetcher(os.environ.get("BINANCE_API_KEY"), "")
    # start_agg_id = fetcher.get_most_recent_historical_agg_id(["/Volumes/Crypto_0/Binance", "/Volumes/Crypto_1/Binance"], 'MATICUSD')
    # print(start_agg_id)
    # fetcher.fetch_all_historical_trades_for_product('MATICUSD', ["/Volumes/Crypto_0/Binance", "/Volumes/Crypto_1/Binance"], start_agg_id=start_agg_id+ 1)
    fetcher.fetch_all_historical_trades_for_product('AAVEUSD', ["/Volumes/Crypto_0/Binance", "/Volumes/Crypto_1/Binance"])
