# 矩阵存储抽象与边界对象
# 本模块提供统一的稠密/稀疏矩阵访问接口（MatrixStorage）、
# 自定义稀疏矩阵（SparseAdjacencyData）和边界值对象（BoundaryObject）。
from __future__ import annotations

from typing import TYPE_CHECKING, List, Tuple

import numpy as np

from .enums import FlatStruct, FlatType, PRCError

try:
    import scipy.sparse as _scipy_sparse  # type: ignore
except Exception:  # pragma: no cover
    _scipy_sparse = None

if TYPE_CHECKING:
    from .order import OrderObject


class BoundaryObject:
    """存储线性顺序的边界值序列，并提供局部极值查找"""

    def __init__(self, size: int = 0, fixed_boundary: float = 0.0) -> None:
        self.fixedBoundary = float(fixed_boundary)
        self.b: List[float] = [0.0] * int(size)

    def size(self) -> int:
        return len(self.b)

    def resize(self, size: int, fixed_boundary: float) -> None:
        self.fixedBoundary = float(fixed_boundary)
        self.b = [0.0] * int(size)

    def at(self, i: int) -> float:
        if i < -1 or i >= self.size():
            raise IndexError("Boundary index out of range")
        if i < 0:
            return self.fixedBoundary
        return self.b[i]

    def set_at(self, i: int, value: float) -> None:
        if i < -1 or i >= self.size():
            raise IndexError("Boundary index out of range")
        if i < 0:
            self.fixedBoundary = float(value)
        else:
            self.b[i] = float(value)

    def data(self) -> List[float]:
        return self.b

    def dataAsVector(self) -> List[float]:
        return self.b

    def Print(self) -> str:
        values = " ".join(str(v) for v in self.b)
        return f"{self.fixedBoundary} | {values}".rstrip()

    def clone(self) -> BoundaryObject:
        other = BoundaryObject()
        other.fixedBoundary = self.fixedBoundary
        other.b = list(self.b)
        return other

    def findLocalMinAndMax(self, marks: List[FlatStruct]) -> None:
        """扫描边界数组，标记交替出现的局部最小值和最大值"""
        p = 0
        marks.clear()
        n = self.size()
        if n <= 0:
            return

        search_min = True
        b0 = self.at(0)
        b_prev = self.at(-1)
        if b0 > b_prev:
            search_min = False
        elif b0 < b_prev:
            search_min = True
        else:
            i = p + 1
            while i < n and self.at(i) == self.at(i - 1):
                i += 1
            if i >= n:
                return
            search_min = self.at(i) < self.at(0)

        while p < n:
            j = p
            if search_min:
                while (j + 1 < n) and (self.at(j) >= self.at(j + 1)):
                    j += 1
                k = j
                while (k > p) and (self.at(k) == self.at(k - 1)):
                    k -= 1
                cur = FlatStruct(k, j, FlatType.LocalMin)
                if j + 1 < n:
                    marks.append(cur)
            else:
                while (j + 1 < n) and (self.at(j) <= self.at(j + 1)):
                    j += 1
                k = j
                while (k > p) and (self.at(k) == self.at(k - 1)):
                    k -= 1
                cur = FlatStruct(k, j, FlatType.LocalMax)
                if (j + 1 < n) or (self.at(k) > self.at(k - 1)):
                    marks.append(cur)
            p = j + 1
            search_min = not search_min


class SparseAdjacencyData:
    """基于字典的自定义稀疏矩阵，每行一个 dict[列号, 值]"""

    def __init__(self, size: int) -> None:
        self.size = int(size)
        self.rows: List[dict[int, float]] = [dict() for _ in range(self.size)]

    @property
    def shape(self) -> Tuple[int, int]:
        return (self.size, self.size)

    def add(self, row: int, col: int, value: float) -> None:
        if value == 0.0:
            return
        bucket = self.rows[row]
        bucket[col] = bucket.get(col, 0.0) + float(value)

    def set(self, row: int, col: int, value: float) -> None:
        bucket = self.rows[row]
        if value == 0.0:
            bucket.pop(col, None)
        else:
            bucket[col] = float(value)

    def get(self, row: int, col: int) -> float:
        return float(self.rows[row].get(col, 0.0))

    def nnz(self) -> int:
        return sum(len(bucket) for bucket in self.rows)

    def to_dense(self) -> np.ndarray:
        dense = np.zeros((self.size, self.size), dtype=float)
        for row, bucket in enumerate(self.rows):
            for col, value in bucket.items():
                dense[row, col] = float(value)
        return dense


class MatrixStorage:
    """统一的稠密/稀疏矩阵访问接口"""

    def __init__(self, matrix: object):
        self.adjMatrix: np.ndarray | None = None
        self.sparseMatrix: SparseAdjacencyData | object | None = None
        self._sparse_kind: str | None = None
        self._degreeCache: np.ndarray | None = None

        if isinstance(matrix, SparseAdjacencyData):
            self.sparseMatrix = matrix
            self._sparse_kind = "custom"
            return

        if _scipy_sparse is not None and _scipy_sparse.issparse(matrix):
            sparse = matrix.tocsc().astype(float)
            if sparse.shape[0] != sparse.shape[1]:
                raise PRCError("Adjacency matrix must be square.")
            self.sparseMatrix = sparse
            self._sparse_kind = "scipy"
            return

        dense = np.asarray(matrix, dtype=float)
        if dense.ndim != 2 or dense.shape[0] != dense.shape[1]:
            raise PRCError("Adjacency matrix must be square.")
        self.adjMatrix = dense

    def rows(self) -> int:
        if self.adjMatrix is not None:
            return int(self.adjMatrix.shape[0])
        if self._sparse_kind == "custom":
            return int(self.sparseMatrix.size)  # type: ignore[union-attr]
        return int(self.sparseMatrix.shape[0])  # type: ignore[union-attr]

    def cols(self) -> int:
        return self.rows()

    def isSparse(self) -> bool:
        return self._sparse_kind is not None

    def nnz(self) -> int:
        if self.adjMatrix is not None:
            return int(np.count_nonzero(self.adjMatrix))
        if self._sparse_kind == "custom":
            return int(self.sparseMatrix.nnz())  # type: ignore[union-attr]
        return int(self.sparseMatrix.nnz)  # type: ignore[union-attr]

    def getCoeff(self, row: int, col: int) -> float:
        if self.adjMatrix is not None:
            return float(self.adjMatrix[row, col])
        if self._sparse_kind == "custom":
            return self.sparseMatrix.get(row, col)  # type: ignore[union-attr]
        return float(self.sparseMatrix[row, col])  # type: ignore[index]

    def setCoeff(self, row: int, col: int, value: float) -> None:
        if self.adjMatrix is not None:
            self.adjMatrix[row, col] = float(value)
        elif self._sparse_kind == "custom":
            self.sparseMatrix.set(row, col, float(value))  # type: ignore[union-attr]
        else:
            self.sparseMatrix[row, col] = float(value)  # type: ignore[index]
        self._degreeCache = None

    def degree(self, idx: int) -> float:
        if self._degreeCache is None:
            if self.adjMatrix is not None:
                self._degreeCache = np.asarray(self.adjMatrix.sum(axis=0), dtype=float).ravel()
            elif self._sparse_kind == "custom":
                degree = np.zeros(self.rows(), dtype=float)
                for bucket in self.sparseMatrix.rows:  # type: ignore[union-attr]
                    for col, value in bucket.items():
                        degree[col] += float(value)
                self._degreeCache = degree
            else:
                self._degreeCache = np.asarray(self.sparseMatrix.sum(axis=0), dtype=float).ravel()  # type: ignore[union-attr]
        return float(self._degreeCache[idx])

    def slope(self, i: int, j: int, order: OrderObject) -> float:
        if i < -1 or i >= order.size() or j < 0 or j >= order.size():
            raise PRCError("slope index out of range")
        target = order.at(j)
        total = self.degree(target) - 2.0 * order.getPrefixCoeff(target, self)
        for p in range(0, i + 1):
            total -= 2.0 * self.getCoeff(order.at(p), target)
        return float(total)

    def calcCuts(
        self,
        startLoc: int,
        mxALoc: int,
        minLoc: int,
        mxBLoc: int,
        stopLoc: int,
        order: OrderObject,
    ) -> Tuple[float, float, float, float]:
        a_int = 0.0
        a_ext = 0.0
        b_int = 0.0
        b_ext = 0.0
        for p in range(startLoc, stopLoc + 1):
            for loc in range(p + 1, stopLoc + 1):
                value = self.getCoeff(order.at(p), order.at(loc))
                if p <= mxALoc and (mxALoc < loc <= minLoc):
                    a_int += value
                if (mxALoc < p <= minLoc) and (minLoc < loc <= stopLoc):
                    a_ext += value
                if (minLoc < p <= mxBLoc) and (mxBLoc < loc <= stopLoc):
                    b_int += value
                if (p <= minLoc) and (minLoc < loc <= mxBLoc):
                    b_ext += value
        return a_int, a_ext, b_int, b_ext


def _to_square_numpy_matrix(a: object) -> object:
    """将各种矩阵格式统一转换为 MatrixStorage 可接受的形式"""
    if isinstance(a, MatrixStorage):
        if a.adjMatrix is not None:
            return a.adjMatrix
        return a.sparseMatrix
    if isinstance(a, SparseAdjacencyData):
        return a
    if _scipy_sparse is not None and _scipy_sparse.issparse(a):
        if a.shape[0] != a.shape[1]:
            raise PRCError("Adjacency matrix must be square")
        return a.tocsc().astype(float)
    if hasattr(a, "toarray"):
        arr = np.asarray(a.toarray(), dtype=float)
    else:
        arr = np.asarray(a, dtype=float)
    if arr.ndim != 2 or arr.shape[0] != arr.shape[1]:
        raise PRCError("Adjacency matrix must be square")
    return arr
