import math

def precision_to_precision_value(precision: int) -> float:
    return 1.0/(10**precision)

def round_float(num: float, precision: int):
    return round(num, precision)

def get_interval_steps(num_start: float, num_end: float, precision: int):
    assert num_end >= num_start, "Number end should be >= num start"
    prevision_number = precision_to_precision_value(precision)
    return math.floor((round_float(num_end, precision) - round_float(num_start, precision)) / prevision_number) + 1
