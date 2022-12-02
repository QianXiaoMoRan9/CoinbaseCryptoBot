from dataclasses import dataclass
import numpy as np


@dataclass
class IOHLCData:
    # timestamp in milliseconds
    timestamp: int
    open: float or np.float64
    close: float or np.float64
    high: float or np.float64
    low: float or np.float64
    volume: float or np.float64

    def __repr__(self):
        return {
            "timestamp": self.timestamp,
            "open": self.open,
            "close": self.close,
            "high": self.high,
            "low": self.low,
            "volume": self.volume
        }
