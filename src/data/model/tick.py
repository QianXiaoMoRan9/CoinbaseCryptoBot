from dataclasses import dataclass

"""
当前一笔交易或者当前时刻的tick
"""
@dataclass
class Tick(object):
    price: float
    volume: float
    cur_time_stamp: int
