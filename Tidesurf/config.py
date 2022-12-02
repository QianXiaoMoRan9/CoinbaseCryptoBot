from Tidesurf.data.constants.exchanges import Exchanges

class Config:
    HISTORICAL_RECORDS_LOCATION_MAP = {
        Exchanges.BINANCE: ["/Volumes/Crypto_0/Binance", "/Volumes/Crypto_1/Binance"],
        Exchanges.COINBASE: ["/Volumes/Crypto_0/Coinbase", "/Volumes/Crypto_1/Coinbase"]
    }