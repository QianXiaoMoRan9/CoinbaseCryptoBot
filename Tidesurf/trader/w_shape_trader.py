from Tidesurf.analytics.indicator.indicator import Indicator
from Tidesurf.trader.trader import Trader
from Tidesurf.config.trader.trader_config import TraderConfig
from typing import List

"""
W shape trader enters when there is a w shape formed.

Entry:
* When the indicator (moving average based) forms a w shape
* and when the current price exceeds the h2 of the w shape

Stop loss:
* When current price below the l2 of the w shape

Stop gain:
* When there is > stop_gain_profit_start_threshold(0.5%) of profit start to record highest profit rate
* When the price falls below stop_gain_exit_threshold(50%) of the highest profit rate, exit
"""

class WShapeTrader(Trader):

    def __init__(self, trader_config: TraderConfig, indicators: List[Indicator], ):
        super().__init__(trader_config, indicators)



