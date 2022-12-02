from dataclasses import dataclass
import numpy as np


@dataclass
class SymbolPositionConfig(object):
    # ex: BTC-USD
    symbol: str
    decay_period_sec: int
    # ex: 0.98
    decay_factor: np.float64
    # ex: "0.01"
    precision: str
