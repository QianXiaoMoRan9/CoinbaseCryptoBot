"""
Integer representation of float to try to overcome float limitations
"""

class Decimal(object):
    precision: int
    value: int

    def __init__(self, num: float, precision: int):
        assert precision >= 0, "Precision should be non-negative"
        self.precision = precision
        self.value = int(num * 10**precision)

    @staticmethod
    def from_value(value, precision):
        res = Decimal(0, precision)
        res.value = value
        return res

    def to_float(self) -> float:
        return self.value * 10**(-self.precision)

    def __add__(self, other):
        other = self._convert_type(other)
        return Decimal.from_value(self.value + other.value, self.precision)

    def __sub__(self, other):
        other = self._convert_type(other)
        return Decimal.from_value(self.value - other.value, self.precision)

    def __mul__(self, other):
        other = self._convert_type(other)
        res = Decimal.from_value(self.value * other.value, self.precision + other.precision)
        return res._change_precision(self.precision)

    def __truediv__(self, other):
        other = self._convert_type(other)
        return Decimal.from_value(int(self.value / other.value), self.precision)

    def __invert__(self):
        return Decimal.from_value(-self.value, self.precision)

    def __repr__(self):
        return f"Decimal({self.value // 10**self.precision}.{self.value % 10**self.precision})"

    def __eq__(self, other):
        if type(other) != Decimal:
            return False
        return self.value == other.value and self.precision == other.precision

    def __gt__(self, other):
        other = self._convert_type(other)
        return self.value > other.value

    def __ge__(self, other):
        other = self._convert_type(other)
        return self.value >= other.value

    def __lt__(self, other):
        other = self._convert_type(other)
        return self.value < other.value

    def __le__(self, other):
        other = self._convert_type(other)
        return self.value <= other.value

    def __hash__(self):
        return hash((self.value, self.precision))

    def _change_precision(self, new_precision: int) -> 'Decimal':
        if new_precision >= self.precision:
            return Decimal.from_value(self.value * 10 ** (new_precision - self.precision), new_precision)
        else:
            return Decimal.from_value(self.value // 10 ** (self.precision - new_precision), new_precision)

    def _convert_type(self, other) -> 'Decimal':
        if type(other) != Decimal:
            if type(other) == float:
                other = Decimal(other, self.precision)
            elif type(other) == int:
                other = Decimal(other * 10**self.precision, self.precision)
            else:
                raise Exception("Unsupported type operation: ", type(other))
        else:
            assert self.precision == other.precision, f"Precision should be the same, this {self.precision}, other: {other.precision}"
        return other
