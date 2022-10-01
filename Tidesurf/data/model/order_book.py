from Tidesurf.data.model.decimal import Decimal
from dataclasses import dataclass
from typing import List
from Tidesurf.data.model.decimal import Decimal

@dataclass
class OrderBook(object):
    # buy 1, buy 2, buy 3, ...
    buy_prices: List[Decimal]
    buy_volume: List[Decimal]
    sell_prices: List[Decimal]
    sell_volume: List[Decimal]
