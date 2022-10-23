import math
from Tidesurf.data.model.decimal import PreciseDecimal
import numpy as np

def precision_to_precision_value(precision: int) -> float:
    return 10 ** (-precision)


def round_float(num: float, precision: int):
    return round(num, precision)


def get_interval_steps(num_start: PreciseDecimal, num_end: PreciseDecimal) -> int:
    assert num_end >= num_start, "Number end should be >= num start"
    return (num_end.value - num_start.value) + 1

def float_almost_equal(number1: np.float64 or float, number2: np.float64 or float, thresh = 0.0000001):
    if type(number1) != np.float64:
        number1 = np.float64(number1)
    if type(number2) != np.float64:
        number2 = np.float64(number2)
    return np.abs(number1 - number2) <= np.float64(thresh)

def decimal_almost_equal(
        number1: np.float64 or float or PreciseDecimal,
        number2: np.float64 or float or PreciseDecimal,
        thresh = 0.0000001):
    if type(number1) != PreciseDecimal:
        number1 = PreciseDecimal.from_float(number1)
    if type(number2) != PreciseDecimal:
        number2 = PreciseDecimal(number2)
    return (number1 - number2).__abs__() <= PreciseDecimal.from_float(thresh)
