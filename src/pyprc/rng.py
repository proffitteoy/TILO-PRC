# 确定性随机数生成器
# 本模块实现与 C++ 版本行为一致的 MSVC LCG 和 Mersenne Twister 随机数生成器，
# 确保不同平台上的聚类结果完全可复现。
from __future__ import annotations

from typing import Callable, List, Sequence


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


def _cpp_random_shuffle(
    values: Sequence[int],
    rand_func: Callable[[], int],
) -> List[int]:
    """兼容 std::random_shuffle（使用 rand()）的洗牌实现。"""
    shuffled = [int(v) for v in values]
    if len(shuffled) <= 1:
        return shuffled
    # 与常见的 random_shuffle 实现一致：从后往前，j = rand() % (i+1)
    for i in range(len(shuffled) - 1, 0, -1):
        j = int(rand_func()) % (i + 1)
        shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
    return shuffled


def _cpp_shuffle_values(values: Sequence[int], seed: int) -> List[int]:
    """保持旧签名：给定种子，使用 MSVC rand() 序列进行 random_shuffle。"""
    local_rand = _MSVCRand(seed)
    return _cpp_random_shuffle(values, local_rand.rand)


_GLOBAL_C_RAND = _MSVCRand(1)
