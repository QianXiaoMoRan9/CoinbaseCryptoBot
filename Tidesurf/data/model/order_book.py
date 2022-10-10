from Tidesurf.data.model.decimal import PreciseDecimal
from dataclasses import dataclass
from typing import List
from Tidesurf.data.model.decimal import PreciseDecimal

@dataclass
class OrderBook(object):
    # buy 1, buy 2, buy 3, ...
    buy_prices: List[PreciseDecimal]
    buy_volumes: List[PreciseDecimal]
    sell_prices: List[PreciseDecimal]
    sell_volumes: List[PreciseDecimal]
