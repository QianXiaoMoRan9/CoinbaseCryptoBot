import requests
from typing import Dict, List

"""
output_dir/
    [symbol]/
        [symbol]_[year]_[month].parquet
"""
class BinanceHistoricalTradeFetcher:
    api_key: str
    output_dir: str

    def __init__(self, api_key: str, output_dir: str):
        self.api_key = api_key
        self.output_dir = output_dir

    def fetch_all_historical_trades_for_product(self, symbol: str, limit: int = 1000):
        # get most recent trades
        pass

    def fetch_historical_trades_for_product(self, symbol: str, from_id: int or None, limit: int = 1000) -> List[Dict]:
        headers = {
            'X-MBX-APIKEY': self.api_key
        }
        if from_id is None:
            resp = requests.get(f'https://api.binance.us/api/v3/aggTrades?symbol={symbol}&limit={limit}')
        else:
            resp = requests.get(
                f'https://api.binance.us/api/v3/aggTrades?symbol={symbol}&fromId={from_id}&limit={limit}')
        return resp.json()
