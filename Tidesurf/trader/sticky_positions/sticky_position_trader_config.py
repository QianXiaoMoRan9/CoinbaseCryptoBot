from dataclasses import dataclass
from Tidesurf.trader.sticky_positions.symbol_position_config import SymbolPositionConfig
from typing import List


@dataclass
class StickyPositionTraderConfig(object):
    historic_data_dir: str
    num_day_historic_data_preload: int
    symbol_position_config_list: List[SymbolPositionConfig]
