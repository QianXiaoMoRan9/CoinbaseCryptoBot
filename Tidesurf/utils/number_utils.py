import math
from Tidesurf.data.model.decimal import Decimal

def precision_to_precision_value(precision: int) -> float:
    return 10 ** (-precision)


def round_float(num: float, precision: int):
    return round(num, precision)


def get_interval_steps(num_start: Decimal, num_end: Decimal) -> int:
    assert num_end >= num_start, "Number end should be >= num start"
    return (num_end.value - num_start.value) + 1
