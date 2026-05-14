# 线性顺序对象
# 本模块定义 OrderObject（节点排列）和 VirtualOrderObject（子排列视图），
# 是 TILO 排序算法操作的核心数据结构。
from __future__ import annotations

from typing import List, MutableSequence, Sequence, Tuple

import numpy as np

from .enums import FlatStruct, FlatType, PRCError
from .matrix import BoundaryObject, MatrixStorage


class OrderObject:
    """节点排列对象，存储排列、逆映射、边界值和极值标记"""

    def __init__(
        self,
        size: int = 0,
        prefix_flag: bool = False,
        data: Sequence[int] | None = None,
        base_start: int = 0,
    ) -> None:
        if data is None:
            self.vdata: List[int] = list(range(size))
        else:
            self.vdata = [int(v) for v in data]
        self._base_start = int(base_start)
        self.ivdata: dict[int, int] = {}
        self.b = BoundaryObject()
        self.m: List[FlatStruct] = []
        self.usePrefix = bool(prefix_flag)
        self.updateInverseOrder()

    def clone(self) -> OrderObject:
        other = OrderObject(data=self.vdata, prefix_flag=self.usePrefix, base_start=self._base_start)
        other.b = self.b.clone()
        other.m = [FlatStruct(mark.start, mark.stop, mark.type) for mark in self.m]
        return other

    def size(self) -> int:
        return len(self.vdata)

    def baseStart(self) -> int:
        return self._base_start

    def at(self, idx: int) -> int:
        return self.vdata[idx]

    def setAt(self, index: int, value: int) -> None:
        self.vdata[index] = int(value)
        self.ivdata[int(value)] = index

    def invAt(self, value: int) -> int:
        try:
            return self.ivdata[int(value)]
        except KeyError as exc:  # pragma: no cover
            raise PRCError(f"Value {value} is not in inverse map.") from exc

    def updateInverseOrder(self) -> None:
        self.ivdata = {value: i for i, value in enumerate(self.vdata)}

    def Print(self) -> str:
        return " ".join(str(v) for v in self.vdata)

    def setFrom(self, src: Sequence[int]) -> None:
        self.vdata = [int(v) for v in src]
        self.updateInverseOrder()
        self.b.resize(len(self.vdata), 0.0)
        self.m.clear()

    def copyTo(self, dest: MutableSequence[int] | np.ndarray) -> None:
        if isinstance(dest, np.ndarray):
            if dest.shape[0] != len(self.vdata):
                raise PRCError("Destination array length does not match order length.")
            dest[:] = np.asarray(self.vdata, dtype=dest.dtype)
            return
        if len(dest) != len(self.vdata):
            raise PRCError("Destination sequence length does not match order length.")
        for i, value in enumerate(self.vdata):
            dest[i] = value

    def boundary(self) -> BoundaryObject:
        return self.b

    def marks(self) -> List[FlatStruct]:
        return self.m

    def getPrefixCoeff(self, node_id: int, matrix: MatrixStorage) -> float:
        return matrix.getCoeff(node_id, 0) if self.usePrefix else 0.0

    def getPrefixDegree(self, matrix: MatrixStorage) -> float:
        return matrix.degree(0) if self.usePrefix else 0.0

    def slope(self, i: int, j: int, matrix: MatrixStorage) -> float:
        return matrix.slope(i, j, self)

    def applyShift(self, p: int, q: int, matrix: MatrixStorage) -> None:
        if p <= q:
            moved = self.vdata[p]
            for x in range(p, q):
                self.setAt(x, self.vdata[x + 1])
            self.setAt(q, moved)
        else:
            moved = self.vdata[p]
            for x in range(p, q, -1):
                self.setAt(x, self.vdata[x - 1])
            self.setAt(q, moved)

    def updateOrder(self, matrix: MatrixStorage, epsilon: float) -> Tuple[int, int]:
        # 延迟导入避免循环依赖
        from .algorithm import calcBoundaries, doShifts
        calcBoundaries(self.b, matrix, self)
        self.b.findLocalMinAndMax(self.m)
        return doShifts(self.m, self, self.b, matrix, epsilon)

    def refineOrder(self, matrix: MatrixStorage, epsilon: float) -> Tuple[int, int]:
        from .algorithm import calcBoundaries, doRShifts
        calcBoundaries(self.b, matrix, self)
        self.b.findLocalMinAndMax(self.m)
        return doRShifts(self.m, self, self.b, matrix, epsilon)

    def split(self, loc: int, reverse_b: bool = False) -> Tuple[OrderObject, OrderObject]:
        if loc < 0 or loc >= self.size():
            raise PRCError("split location out of range")
        a_data = self.vdata[: loc + 1]
        b_data = self.vdata[loc + 1 :]
        if reverse_b:
            b_data = list(reversed(b_data))
        a = OrderObject(data=a_data, prefix_flag=self.usePrefix, base_start=self.baseStart())
        b = OrderObject(
            data=b_data,
            prefix_flag=self.usePrefix,
            base_start=self.baseStart() + loc + 1,
        )
        return a, b


# --- PLACEHOLDER_VIRTUAL_ORDER ---


class VirtualOrderObject(OrderObject):
    """OrderObject 的子视图，直接操作父排列的一段区间"""

    def __init__(self, storage: OrderObject, start: int = 0, size: int | None = None) -> None:
        self.storage = storage
        self._start = int(start)
        self._size = storage.size() - self._start if size is None else int(size)
        if self._start < 0 or self._size < 0 or (self._start + self._size) > storage.size():
            raise PRCError("Invalid virtual order range.")
        self.b = BoundaryObject()
        self.m: List[FlatStruct] = []
        self.usePrefix = storage.usePrefix

    @property
    def vdata(self) -> List[int]:
        return [self.at(i) for i in range(self.size())]

    def clone(self) -> VirtualOrderObject:
        other = VirtualOrderObject(self.storage, self._start, self._size)
        other.b = self.b.clone()
        other.m = [FlatStruct(mark.start, mark.stop, mark.type) for mark in self.m]
        other.usePrefix = self.usePrefix
        return other

    def size(self) -> int:
        return self._size

    def baseStart(self) -> int:
        return self._start

    def at(self, idx: int) -> int:
        if idx < 0 or idx >= self.size():
            raise PRCError("Virtual order index out of range.")
        return self.storage.at(self._start + idx)

    def setAt(self, index: int, value: int) -> None:
        if index < 0 or index >= self.size():
            raise PRCError("Virtual order index out of range.")
        self.storage.setAt(self._start + index, value)

    def invAt(self, value: int) -> int:
        return self.storage.invAt(value) - self._start

    def updateInverseOrder(self) -> None:
        for i in range(self.size()):
            self.setAt(i, self.at(i))

    def Print(self) -> str:
        return " ".join(str(self.at(i)) for i in range(self.size()))

    def setFrom(self, src: Sequence[int]) -> None:
        if len(src) != self.size():
            raise PRCError("Invalid order size for copying.")
        for i, value in enumerate(src):
            self.setAt(i, int(value))

    def copyTo(self, dest: MutableSequence[int] | np.ndarray) -> None:
        if isinstance(dest, np.ndarray):
            if dest.shape[0] != self.size():
                raise PRCError("Destination array length does not match order length.")
            dest[:] = np.asarray(self.vdata, dtype=dest.dtype)
            return
        if len(dest) != self.size():
            raise PRCError("Destination sequence length does not match order length.")
        for i in range(self.size()):
            dest[i] = self.at(i)

    def boundary(self) -> BoundaryObject:
        return self.b

    def marks(self) -> List[FlatStruct]:
        return self.m

    def getPrefixCoeff(self, node_id: int, matrix: MatrixStorage) -> float:
        return matrix.getCoeff(node_id, 0) if self.usePrefix else 0.0

    def getPrefixDegree(self, matrix: MatrixStorage) -> float:
        return matrix.degree(0) if self.usePrefix else 0.0

    def slope(self, i: int, j: int, matrix: MatrixStorage) -> float:
        return matrix.slope(i, j, self)

    def applyShift(self, p: int, q: int, matrix: MatrixStorage) -> None:
        if p <= q:
            moved = self.at(p)
            for x in range(p, q):
                self.setAt(x, self.at(x + 1))
            self.setAt(q, moved)
        else:
            moved = self.at(p)
            for x in range(p, q, -1):
                self.setAt(x, self.at(x - 1))
            self.setAt(q, moved)

    def split(self, loc: int, reverse_b: bool = False) -> Tuple[VirtualOrderObject, VirtualOrderObject]:
        if loc < 0 or loc >= self.size():
            raise PRCError("split location out of range")
        a = VirtualOrderObject(self.storage, self._start, loc + 1)
        b = VirtualOrderObject(self.storage, self._start + loc + 1, self.size() - loc - 1)
        a.usePrefix = self.usePrefix
        b.usePrefix = self.usePrefix
        if reverse_b:
            reversed_values = [b.at(i) for i in range(b.size() - 1, -1, -1)]
            for idx, value in enumerate(reversed_values):
                b.setAt(idx, value)
        a.updateInverseOrder()
        b.updateInverseOrder()
        return a, b
