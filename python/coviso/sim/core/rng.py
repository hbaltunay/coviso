import math
import random

K_PI: float = 3.14159265358979323846


class Rng:
    def __init__(self, master: int, stream: int) -> None:
        seed_val = self._splitmix(
            (master ^ self._splitmix(stream)) & 0xFFFFFFFFFFFFFFFF
        )
        self._eng = random.Random(seed_val)

    def u01(self) -> float:
        rand_bits = self._eng.getrandbits(64) >> 11
        return float(rand_bits) * (1.0 / 9007199254740992.0)

    def uniform(self, a: float, b: float) -> float:
        return a + (b - a) * self.u01()

    def uniform_int(self, a: int, b: int) -> int:
        return min(b, a + int(self.u01() * (b - a + 1)))

    def bernoulli(self, p: float) -> bool:
        return self.u01() < p

    def normal(self, mean: float, sd: float) -> float:
        u1 = max(self.u01(), 1e-300)
        u2 = self.u01()
        return mean + sd * math.sqrt(-2.0 * math.log(u1)) * math.cos(
            2.0 * K_PI * u2
        )

    def trunc_normal(
        self, mean: float, sd: float, lo: float, hi: float
    ) -> float:
        for _ in range(32):
            x = self.normal(mean, sd)
            if lo <= x <= hi:
                return x
        return max(lo, min(mean, hi))

    def log_normal(self, median: float, sigma: float) -> float:
        return median * math.exp(self.normal(0.0, sigma))

    def shuffle[T](self, v: list[T]) -> None:
        for i in range(len(v), 1, -1):
            idx = self.uniform_int(0, i - 1)
            v[i - 1], v[idx] = v[idx], v[i - 1]

    @staticmethod
    def _splitmix(z: int) -> int:
        z = (z + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
        return (z ^ (z >> 31)) & 0xFFFFFFFFFFFFFFFF
