"""
This module contains the class to persist trades into SQLite
"""
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Double
from sqlalchemy.orm import relationship

from Tidesurf.database.base import _DECL_BASE

logger = logging.getLogger(__name__)


class Order(_DECL_BASE):
    """
    Order database model
    Keeps a record of all orders placed on the exchange_adapter

    One to many relationship with Trades:
      - One trade can have many orders
      - One Order can only be associated with one Trade

    Mirrors CCXT Order structure
    """
    __tablename__ = 'orders'

    use_db: bool = True
    # ID PK of the order
    id = Column(Integer, primary_key=True)
    # Trade ID FK
    trade_id = Column(Integer, ForeignKey('trades.id'), index=True)
    trade = relationship("Trade", back_populates="orders")

    # order ID that the exchange_adapter is given back
    order_id: str = Column(String(255), nullable=True)

    # number of instrument
    amount = Column(Double, nullable=False)
    # Price the order is placed at
    price = Column(Double, nullable=False)
    # Average price of order filled
    average = Column(Double, nullable=False)
    # date time the order is placed
    order_datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    # date time the order is placed
    order_filled_datetime = Column(DateTime, nullable=True)

    @staticmethod
    def commit():
        Order.query.session.commit()

    @staticmethod
    def rollback():
        Order.query.session.rollback()

    def __repr__(self):

        return (f'Order(id={self.id}, order_id={self.order_id}, trade_id={self.trade_id}, '
                f'side={self.side}, order_type={self.order_type}, status={self.status}), order_intent={self.order_intent}')

    @staticmethod
    def order_by_id(order_id: str) -> Optional['Order']:
        """
        Retrieve order based on order_id
        :return: Order or None
        """
        return Order.query.filter(Order.order_id == order_id).first()


class Trade(_DECL_BASE):
    """
    Trade database model.
    Also handles updating and querying trades

    Note: Fields must be aligned with LocalTrade class
    """
    __tablename__ = 'trades'

    use_db: bool = True

    id = Column(Integer, primary_key=True)

    orders = relationship("Order", order_by="Order.id", cascade="all, delete-orphan", lazy="joined")

    exchange = Column(String(25), nullable=False)

    symbol = Column(String(25), nullable=False, index=True)

    # amount of total planned exposed positions this trade will be included
    amount = Column(Double, nullable=False)
    price = Column(Double, nullable=False)
    open_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    # order type: market, limit, stop_limit
    trade_type = Column(String(50), nullable=False)
    trade_side = Column(String(50), nullable=False)
    # Intention of the trade:
    trade_intent: str = Column(String(50), nullable=False)
    # Status: pending, partially filled, filled, canceled
    status = Column(String(255), nullable=True, index=True)
    # absolute value of the stop loss
    stop_loss = Column(Double, nullable=False)
    # percentage value of the stop loss
    stop_loss_pct = Column(Double, nullable=False)

    is_short = Column(Boolean, nullable=False, default=False)

    # Mode of trades defined by TradeMode
    trade_mode = Column(String(50), nullable=False)
    strategy = Column(String(100), nullable=True)
    # trade id returned by the exchange
    trade_id = Column(String(255), nullable=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.realized_profit = 0
        self.recalc_open_trade_value()

    def delete(self) -> None:

        for order in self.orders:
            Order.query.session.delete(order)

        Trade.query.session.delete(self)
        Trade.commit()

    @staticmethod
    def commit():
        Trade.query.session.commit()

    @staticmethod
    def rollback():
        Trade.query.session.rollback()

class Cash(_DECL_BASE):
    """
    Trade database model.
    Also handles updating and querying trades

    Note: Fields must be aligned with LocalTrade class
    """
    __tablename__ = 'cash'

    use_db: bool = True

    id = Column(Integer, primary_key=True)

    amount = Column(Double, nullable=False)

    update_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    @staticmethod
    def commit():
        Cash.query.session.commit()

    @staticmethod
    def rollback():
        Cash.query.session.rollback()

    @staticmethod
    def get_cash() -> float:
        """
        Returns all open trades
        NOTE: Not supported in Backtesting.
        """
        return Cash.query.order_by(Cash.update_date.desc()).limit(1)[0].amount

    @staticmethod
    def update_cash(amount: float):
        cash = Cash(amount=amount, update_date = datetime.utcnow())
        Cash._session.add_all([cash])
        Cash.commit()

class ExchangeSimulatorCash(_DECL_BASE):
    """
    Trade database model.
    Also handles updating and querying trades

    Note: Fields must be aligned with LocalTrade class
    """
    __tablename__ = 'exchange_simulator_cash'

    use_db: bool = True

    id = Column(Integer, primary_key=True)

    amount = Column(Double, nullable=False)

    update_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    @staticmethod
    def commit():
        ExchangeSimulatorCash.query.session.commit()

    @staticmethod
    def rollback():
        ExchangeSimulatorCash.query.session.rollback()

    @staticmethod
    def get_cash() -> float:
        """
        Returns all open trades
        NOTE: Not supported in Backtesting.
        """
        return ExchangeSimulatorCash.query.order_by(ExchangeSimulatorCash.update_date.desc()).limit(1)[0].amount

    @staticmethod
    def update_cash(amount: float):
        cash = ExchangeSimulatorCash(amount=amount, update_date = datetime.utcnow())
        ExchangeSimulatorCash._session.add_all([cash])
        ExchangeSimulatorCash.commit()

class ExchangeSimulatorOrder(_DECL_BASE):
    """
    Order database model
    Keeps a record of all orders placed on the exchange_adapter

    One to many relationship with Trades:
      - One trade can have many orders
      - One Order can only be associated with one Trade

    Mirrors CCXT Order structure
    """
    __tablename__ = 'exchange_simulator_orders'

    use_db: bool = True
    # ID PK of the order
    id = Column(Integer, primary_key=True)
    # Trade ID FK
    trade_id = Column(Integer, ForeignKey('exchange_simulator_trades.id'), index=True)
    trade = relationship("ExchangeSimulatorTrade", back_populates="exchange_simulator_orders")

    # order ID that the exchange_adapter is given back
    order_id: str = Column(String(255), nullable=True)
    # number of instrument
    amount = Column(Double, nullable=True)
    # Price the order is placed at
    price = Column(Double, nullable=True)
    # date time the order is placed
    order_filled_datetime = Column(DateTime, nullable=False, default=datetime.utcnow)

class ExchangeSimulatorTrade(_DECL_BASE):
    """
    Trade database model.
    Also handles updating and querying trades

    Note: Fields must be aligned with LocalTrade class
    """
    __tablename__ = 'exchange_simulator_trades'

    use_db: bool = True

    id = Column(Integer, primary_key=True)

    exchange_simulator_orders = relationship("ExchangeSimulatorOrder", order_by="ExchangeSimulatorOrder.id", cascade="all, delete-orphan", lazy="joined")

    exchange = Column(String(25), nullable=False)

    symbol = Column(String(25), nullable=False, index=True)

    # amount of total planned exposed positions this trade will be included
    amount = Column(Double, nullable=False)
    open_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    # order type: market, limit, stop_limit
    trade_type = Column(String(50), nullable=False)
    trade_side = Column(String(50), nullable=False)
    # Status: pending, partially filled, filled, canceled
    status = Column(String(255), nullable=True, index=True)
