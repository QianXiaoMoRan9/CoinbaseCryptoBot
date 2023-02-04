from enum import StrEnum


class TradeStatus(StrEnum):
    PENDING = "PENDING"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"


class TradeSide(StrEnum):
    BUY = "BUY"
    SELL = 'SELL'


class TradeType(StrEnum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS_LIMIT = "STOP_LOSS_LIMIT"
    TAKE_PROFIT_LIMIT = "TAKE_PROFIT_LIMIT"
    LIMIT_MAKER = "LIMIT_MAKER"


class TradeIntent(StrEnum):
    ENTRY = "ENTRY"
    ADD_UP = "ADD_UP"
    STOP_LOSS = "STOP_LOSS"
    STOP_GAIN = "STOP_GAIN"
    EXIT = "EXIT"


class TradeMode(StrEnum):
    BACK_TESTING = "BACK_TESTING"
    DRY_RUN = "DRY_RUN"
    LIVE = "LIVE"


class TradeStatus(StrEnum):
    ACKNOWLEDGED = "ACKNOWLEDGED"
    PENDING = "PENDING"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"

