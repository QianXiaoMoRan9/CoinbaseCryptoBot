import uuid
import numpy as np

class Position(object):
    id_: str
    symbol: str
    price: np.float64
    volume: np.float64 or int
    stop_loss: np.float64
    target_price: np.float64

    def __init_(self,
                symbol: str,
                price: np.float64,
                volume: int or np.float64,
                stop_loss: np.float64,
                target_price: np.float64):
        self.id_ = uuid.uuid4().hex
        self.symbol = symbol
        self.price = price
        self.volume = volume
        self.stop_loss = stop_loss
        self.target_price = target_price

    def __eq__(self, other):
        assert type(other) == Position
        return self.id_ == other.id_

    def __hash__(self):
        return hash(self.id_)

    def __repr__(self):
        return str({
            "id": self.id_,
            "symbol": self.symbol,
            "price": self.price,
            "volume": self.volume,
            "stop_loss": self.stop_loss,
            "target_price": self.target_price
        })

