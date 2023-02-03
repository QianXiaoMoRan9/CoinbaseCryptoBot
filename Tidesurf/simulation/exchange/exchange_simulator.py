"""
TODO: Keep track of the cash inside exchange wallet
TODO: Make the order create request async. Currently it is filled immediately
"""
from sqlalchemy.orm import Session
import uuid

from Tidesurf.database.enums import TradeStatus
from Tidesurf.database.model import ExchangeSimulatorCash, ExchangeSimulatorOrder, ExchangeSimulatorTrade
from Tidesurf.service.model.trade_models import CreateTradeResponse

class ExchangeSimulator:
    db_session: Session
    exchange: str

    def __init__(self, db_session: Session, exchange: str):
        self.db_session = db_session
        self.exchange = exchange

    def create_trade_handler(self, symbol: str, trade_side: str, trade_type: str, quantity: float, price: float):
        # make data store available inside the database
        with self.db_session.begin():
            try:
                remaining_cash = ExchangeSimulatorCash.get_cash()
                if remaining_cash < quantity * price:
                    return CreateTradeResponse(
                        trade_status=TradeStatus.ACKNOWLEDGED,
                        id=0,
                        quantity=quantity,
                        price=price,
                        exchange=self.exchange,
                        symbol=symbol,
                        trade_id=""
                    )
                trade = ExchangeSimulatorTrade(
                    exchange=self.exchange,
                    symbol=symbol,
                    amount=quantity,
                    trade_type=trade_type,
                    trade_side=trade_side,
                    status=TradeStatus.FILLED
                )
                self.db_session.add(trade)
                self.db_session.flush()
                order = ExchangeSimulatorOrder(
                    trade_id=trade.id,
                    order_id=uuid.uuid4().hex,
                    amount=quantity,
                    price=price,
                )
                self.db_session.add(order)
                cash = ExchangeSimulatorCash(
                    amount=remaining_cash - quantity * price
                )
                self.db_session.add(cash)
            except:
                self.db_session.rollback()
                raise
            else:
                self.db_session.commit()
        return CreateTradeResponse(
            id=trade.id,
            trade_status=TradeStatus.ACKNOWLEDGED,
            quantity=quantity,
            price=price,
            symbol=symbol,
            exchange=self.exchange,
            trade_id=""
        )

    def get_trade_handler(self, id_: int) -> ExchangeSimulatorTrade:
        with self.db_session.begin():
            result = ExchangeSimulatorTrade.query.filter_by(id=id_)
            return result[0]

    def cancel_order_handler(self):
        pass
