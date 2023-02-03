from dataclasses import dataclass
from Tidesurf.database.enums import TradeStatus
from datetime import datetime
from typing import List

@dataclass
class CreateTradeResponse:
    trade_status: TradeStatus
    id: int
    quantity: float
    price: float
    exchange: str
    symbol: str
    trade_id: str


@dataclass
class GetOrderResponse:
    id: int
    amount: float
    price: float
    order_filled_datetime: datetime


@dataclass
class GetTradeResponse:
    id: int
    trade_status: TradeStatus
    quantity: float
    price: float
    exchange: str
    symbol: str
    trade_id: str
    orders: List[GetOrderResponse]
