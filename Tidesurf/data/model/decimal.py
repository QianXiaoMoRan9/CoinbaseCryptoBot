"""
Integer representation of float to try to overcome float limitations
"""
from decimal import Decimal as NativeDecimal
from decimal import localcontext
import numpy as np

class PreciseDecimal(NativeDecimal):

    @staticmethod
    def precision_float(precision: int) -> 'PreciseDecimal':
        assert precision > 0, "Precision must ba a non zero int"
        assert type(precision) == int, "Precision mush be of type int"
        return PreciseDecimal(f"0.{'0' * (precision - 1)}1")

    @staticmethod
    def localcontext():
        return localcontext()

    @staticmethod
    def from_float_precise(value: float, precision: int) -> 'PreciseDecimal':
        PreciseDecimal._verify_precision(precision)
        assert type(value) == float or type(value) == np.float32 or type(value) == np.float64, "Value type must be float"
        int_value = str(int(value * 10**precision))
        num_length = len(int_value)
        return PreciseDecimal(f"{int_value[: num_length - precision]}.{int_value[num_length - precision:]}")

    @staticmethod
    def _verify_precision(precision):
        assert type(precision) == int, "Precision must be of type int"
        assert precision > 0, "Precision must be non negative"

    def to_float(self) -> float:
        return np.float64(self)

    def __add__(self, other):
        return PreciseDecimal(super().__add__(other))

    def __sub__(self, other):
        return PreciseDecimal(super().__sub__(other))

    def __mul__(self, other):
        return PreciseDecimal(super().__mul__(other))

    def __truediv__(self, other):
        return PreciseDecimal(super().__truediv__(other))

    def __divmod__(self, other):
        res = super().__divmod__(other)
        return PreciseDecimal(res[0]), PreciseDecimal(res[1])

    def __abs__(self):
        return PreciseDecimal(super().__abs__())



