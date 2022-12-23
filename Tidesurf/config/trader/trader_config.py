from dataclasses import dataclass
from typing import List


@dataclass
class TraderConfig:
    symbol: str
    historic_data_dir: str
    num_day_historic_data_preload: int
    trading_symbols: List[str]
