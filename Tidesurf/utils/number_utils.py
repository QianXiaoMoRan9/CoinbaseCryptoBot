import math
from Tidesurf.data.model.decimal import PreciseDecimal

def precision_to_precision_value(precision: int) -> float:
    return 10 ** (-precision)


def round_float(num: float, precision: int):
    return round(num, precision)


def get_interval_steps(num_start: PreciseDecimal, num_end: PreciseDecimal) -> int:
    assert num_end >= num_start, "Number end should be >= num start"
    return (num_end.value - num_start.value) + 1
