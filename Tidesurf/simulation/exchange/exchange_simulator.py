"""
TODO: Keep track of the cash inside exchange wallet
TODO: Make the order create request async. Currently it is filled immediately
"""
from sqlalchemy.orm import scoped_session
import uuid
from datetime import datetime
from Tidesurf.database.enums import TradeStatus, TradeType, TradeSide
from Tidesurf.database.model import ExchangeSimulatorCash, ExchangeSimulatorOrder, ExchangeSimulatorTrade
from Tidesurf.service.model.trade_models import CreateTradeResponse

class ExchangeSimulator:
    db_session: scoped_session
    exchange: str

    def __init__(self, db_session: scoped_session, exchange: str):
        self.db_session = db_session
        self.exchange = exchange

    def create_trade_handler(self, symbol: str, trade_side: TradeSide, trade_type: TradeType, quantity: float, price: float):
        # make data store available inside the database
        local_session = self.db_session()
        with local_session.begin():
            try:
                remaining_cash = ExchangeSimulatorCash.get_cash(local_session)
                if remaining_cash < quantity * price:
                    return CreateTradeResponse(
                        trade_status=TradeStatus.REJECTED,
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
                    open_date=datetime.utcnow(),
                    trade_type=trade_type,
                    trade_side=trade_side,
                    status=TradeStatus.FILLED
                )
                local_session.add(trade)
                local_session.flush()
                order = ExchangeSimulatorOrder(
                    trade_id=trade.id,
                    order_id=uuid.uuid4().hex,
                    amount=quantity,
                    price=price,
                )
                local_session.add(order)
                ExchangeSimulatorCash.update_cash(
                    local_session,
                    amount=remaining_cash - quantity * price
                )
            except:
                local_session.rollback()
                local_session.close()
                raise
            else:
                trade_id = trade.id
                self.db_session.commit()
                local_session.close()
                return CreateTradeResponse(
                    id=trade_id,
                    trade_status=TradeStatus.ACKNOWLEDGED,
                    quantity=quantity,
                    price=price,
                    symbol=symbol,
                    exchange=self.exchange,
                    trade_id=""
                )

    def get_trade_handler(self, id_: int) -> ExchangeSimulatorTrade:
        local_session = self.db_session()
        result = local_session.query(ExchangeSimulatorTrade).filter_by(id=id_)
        return result[0]

    def cancel_order_handler(self):
        pass
