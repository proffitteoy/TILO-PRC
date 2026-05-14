# 确定性随机数生成器
# 本模块实现与 C++ 版本行为一致的 MSVC LCG 和 Mersenne Twister 随机数生成器，
# 确保不同平台上的聚类结果完全可复现。
from __future__ import annotations

from typing import List, Sequence


class _MSVCRand:
    """兼容经典 MSVC rand()/srand() 随机数序列"""

    def __init__(self, seed: int = 1) -> None:
        self._state = 1
        self.srand(seed)

    def srand(self, seed: int) -> None:
        self._state = int(seed) & 0xFFFFFFFF

    def rand(self) -> int:
        self._state = (self._state * 214013 + 2531011) & 0xFFFFFFFF
        return (self._state >> 16) & 0x7FFF


class _MT19937Compat:
    """兼容 C++ std::mt19937 的 Mersenne Twister 实现"""
    N = 624
    M = 397
    MATRIX_A = 0x9908B0DF
    UPPER_MASK = 0x80000000
    LOWER_MASK = 0x7FFFFFFF

    def __init__(self, seed: int) -> None:
        self.mt = [0] * self.N
        self.mti = self.N + 1
        self.seed(seed)

    def seed(self, seed: int) -> None:
        self.mt[0] = int(seed) & 0xFFFFFFFF
        for i in range(1, self.N):
            prev = self.mt[i - 1]
            self.mt[i] = (1812433253 * (prev ^ (prev >> 30)) + i) & 0xFFFFFFFF
        self.mti = self.N

    def rand_uint32(self) -> int:
        mag01 = [0, self.MATRIX_A]
        if self.mti >= self.N:
            for kk in range(self.N - self.M):
                y = (self.mt[kk] & self.UPPER_MASK) | (self.mt[kk + 1] & self.LOWER_MASK)
                self.mt[kk] = self.mt[kk + self.M] ^ (y >> 1) ^ mag01[y & 0x1]
            for kk in range(self.N - self.M, self.N - 1):
                y = (self.mt[kk] & self.UPPER_MASK) | (self.mt[kk + 1] & self.LOWER_MASK)
                self.mt[kk] = self.mt[kk + (self.M - self.N)] ^ (y >> 1) ^ mag01[y & 0x1]
            y = (self.mt[self.N - 1] & self.UPPER_MASK) | (self.mt[0] & self.LOWER_MASK)
            self.mt[self.N - 1] = self.mt[self.M - 1] ^ (y >> 1) ^ mag01[y & 0x1]
            self.mti = 0

        y = self.mt[self.mti]
        self.mti += 1
        y ^= y >> 11
        y ^= (y << 7) & 0x9D2C5680
        y ^= (y << 15) & 0xEFC60000
        y ^= y >> 18
        return y & 0xFFFFFFFF


def _uniform_int_mt19937(rng: _MT19937Compat, upper_inclusive: int) -> int:
    if upper_inclusive <= 0:
        return 0
    bucket_count = upper_inclusive + 1
    scale = (1 << 32) // bucket_count
    limit = scale * bucket_count
    while True:
        value = rng.rand_uint32()
        if value < limit:
            return value // scale


def _cpp_shuffle_values(values: Sequence[int], seed: int) -> List[int]:
    """使用 C++ 兼容的 Fisher-Yates 洗牌算法"""
    shuffled = [int(v) for v in values]
    if len(shuffled) <= 1:
        return shuffled
    rng = _MT19937Compat(seed)
    for i in range(1, len(shuffled)):
        j = _uniform_int_mt19937(rng, i)
        shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
    return shuffled


_GLOBAL_C_RAND = _MSVCRand(1)
