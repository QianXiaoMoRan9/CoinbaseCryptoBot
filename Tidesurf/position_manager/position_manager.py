from abc import ABC, abstractmethod
import numpy as np
from multiprocessing import Lock
import functools
from datetime import datetime
from Tidesurf.database.enums import TradeMode, OrderIntent, OrderStatus, OrderSide, OrderType
from Tidesurf.database.model import Trade, Order
from typing import Tuple

DB_LOCK = Lock()


def synchronized(wrapped):
    global DB_LOCK

    @functools.wraps(wrapped)
    def _wrapper(*args, **kwargs):
        with DB_LOCK:
            return wrapped(*args, **kwargs)

    return _wrapper


class PositionManager(ABC):
    REJECT_QUANTITY = None

    def __init__(self):
        pass

    @abstractmethod
    @synchronized
    def get_instrument_quantity(self, price: float or np.float64, accept_partial: bool) -> float:
        pass

    @staticmethod
    @synchronized
    def create_trade(
            symbol: str,
            exchange: str,
            price: np.float64 or float,
            quantity: float or np.float64,
            stop_loss: float or np.float64,
            strategy: str,
            is_short: bool,
            trade_mode: str) -> Tuple[int, int]:
        order = Order(
            symbol=symbol,
            order_id="",
            order_intent=OrderIntent.ENTRY,
            status=OrderStatus.PENDING,
            side=OrderSide.BUY if not is_short else OrderSide.SELL,
            amount=quantity,
            filled=0,
            price=price,
            average=0,
            order_datetime=datetime.utcnow(),
            order_type=OrderType.MARKET
        )
        trade = Trade(
            exchange=exchange,
            symbol=symbol,
            amount=quantity,
            open_date=datetime.utcnow(),
            stop_loss=stop_loss,
            stop_loss_pct=stop_loss/price,
            strategy=strategy,
            is_short=is_short,
            trade_mode=trade_mode
        )
        trade.orders.append(order)
        Trade._session.add(trade)
        Trade._session.add(order)
        Trade._session.commit()
        Trade._session.flush()
        return order.id, trade.id


    @staticmethod
    def is_accepted_position(quantity: float or None):
        return quantity is not None
