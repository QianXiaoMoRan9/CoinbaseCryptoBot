from dataclasses import dataclass
import numpy as np
"""
当前一笔交易或者当前时刻的tick
"""
@dataclass
class Tick(object):
    price: np.float64
    volume: np.float64
    cur_time_stamp: int
