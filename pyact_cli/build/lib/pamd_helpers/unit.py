class Unit:
    def __init__(self, value: float, unit: str):
        self.value: float = value
        self.unit: str = unit

    def __repr__(self) -> str:
        return f"{self.value} {self.unit}"
        
    def _extract(self, other) -> float:
        return float(other.value) if isinstance(other, Unit) else float(other)

    def __add__(self, other):
        return float(self.value) + self._extract(other)

    def __radd__(self, other):
        return self._extract(other) + float(self.value)

    def __sub__(self, other):
        return float(self.value) - self._extract(other)

    def __rsub__(self, other):
        return self._extract(other) - float(self.value)

    def __mul__(self, other):
        return float(self.value) * self._extract(other)

    def __rmul__(self, other):
        return self._extract(other) * float(self.value)

    def __truediv__(self, other):
        return float(self.value) / self._extract(other)

    def __rtruediv__(self, other):
        return self._extract(other) / float(self.value)

    def __pow__(self, power):
        return float(self.value) ** self._extract(power)

    def __neg__(self):
        return -float(self.value)
        
    def __abs__(self):
        return abs(float(self.value))
