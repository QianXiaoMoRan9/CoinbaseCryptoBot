import os
import logging
from Tidesurf.data.executor.execute_get_monthly_data import execute_get_monthly_data_for_product
from Tidesurf.data.post_processing.data_cleanup import raw_data_cleanup, verify_cleanup
# from server.websocket_feed import start_job
from Tidesurf.analytics.positions import get_interval_market_positions
from pprint import pprint
from datetime import datetime
from Tidesurf.data.exchange.binance.binance_trade_fetcher import BinanceTradeFetcher
if __name__ == "__main__":
    LOG_PATH = "log"
    if not os.path.exists(LOG_PATH):
        os.mkdir(LOG_PATH)
    today = datetime.today()
    LOG_FILE = f"{LOG_PATH}/{today.year}-{today.month}-{today.day}.log"
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO, filemode='a')


    # execute_get_monthly_data_for_product("SOL-USD", "./raw")
    # raw_data_cleanup('./raw', './processed', 'ETH-USD', 2019, 1, 2022, 7)
    # verify_cleanup('./processed', 'ETH-USD', 2018, 12, 2022, 7)

    # start_job()
    # pprint(get_interval_market_positions('./processed', 'ETH-USD', 1548978840, 1580509200))
    # exchange = BinanceHistoricalTradeFetcher(os.environ.get("BINANCE_API_KEY"), "")
    # response = exchange.fetch_historical_trades_for_product("BTCUSD", 0)
    # print(datetime.fromtimestamp(response[0]['T'] // 1000), response[0]['a'], response[0]['f'])
    # print(datetime.fromtimestamp(response[-1]['T'] // 1000), response[-1]['a'], response[-1]['f'])


    ### Fetch crypto all historic records, Binance
    SYMBOL = "UNIUSD"
    fetcher = BinanceTradeFetcher(os.environ.get("BINANCE_API_KEY"), "")
    fetcher.fetch_all_historical_trades_for_product(SYMBOL, ["/Volumes/Crypto_0/Binance", "/Volumes/Crypto_1/Binance"])



    ### load data
    # from Tidesurf.data.exchange.binance.binance_trade_loader import BinanceTradeGenerativeLoader
    # from Tidesurf.analytics.indicators.ema import EMA
    # from datetime import datetime
    #
    # dt = datetime(2022, 11, 20, 0, 0, 1)
    # binance_loader = BinanceTradeGenerativeLoader(
    #     ["/Volumes/Crypto_0/Binance", "/Volumes/Crypto_1/Binance"],
    #     "MATICUSD",
    #     int(dt.timestamp())
    # )
    # ema = EMA(60, 3, int(dt.timestamp()))
    #
    # while binance_loader.has_next():
    #     data = binance_loader.next()
    #     # print("Append timestamp: ", data[1])
    #     ema.append(data[1], [data[2], data[3]])
    #
    # print(ema.indicator_values)


