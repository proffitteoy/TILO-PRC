# 旧版兼容函数
# 本模块保留从 C++ 扩展时代遗留的兼容函数，均已标记弃用。
from __future__ import annotations

import warnings
from typing import MutableSequence, Sequence

import numpy as np

from .algorithm import TILO, calcBoundaries, pinchRatioClustering
from .order import OrderObject
from .structs import PrcCountsStruct, PrcPolicyStruct, PrcReturnStruct, TiloPolicyStruct

ivec = list
dvec = list


def sparse_pinchRatioClustering(
    matrix_like: object,
    order_like: OrderObject | MutableSequence[int] | np.ndarray,
    labels_like: MutableSequence[int] | np.ndarray,
    k: int,
    policy: PrcPolicyStruct,
) -> PrcReturnStruct:
    warnings.warn("sparse_pinchRatioClustering 已弃用，请直接使用 pinchRatioClustering", DeprecationWarning, stacklevel=2)
    return pinchRatioClustering(matrix_like, order_like, labels_like, k, policy)


def sparse_TILO(
    matrix_like: object,
    order_like: OrderObject,
    policy: TiloPolicyStruct | None = None,
) -> PrcCountsStruct:
    warnings.warn("sparse_TILO 已弃用，请直接使用 TILO", DeprecationWarning, stacklevel=2)
    return TILO(matrix_like, order_like, policy)


def sparse_calcBoundaries(matrix_like: object, order_like: OrderObject) -> None:
    warnings.warn("sparse_calcBoundaries 已弃用，请直接使用 calcBoundaries", DeprecationWarning, stacklevel=2)
    calcBoundaries(matrix_like, order_like)


def ivecAt(v: Sequence[int], i: int) -> int:
    warnings.warn("ivecAt 已弃用，请直接使用索引访问", DeprecationWarning, stacklevel=2)
    return int(v[i])


def ivecSet(v: MutableSequence[int], i: int, value: int) -> None:
    warnings.warn("ivecSet 已弃用，请直接使用索引赋值", DeprecationWarning, stacklevel=2)
    v[i] = int(value)


def dvecAt(v: Sequence[float], i: int) -> float:
    warnings.warn("dvecAt 已弃用，请直接使用索引访问", DeprecationWarning, stacklevel=2)
    return float(v[i])


def dvecSet(v: MutableSequence[float], i: int, value: float) -> None:
    warnings.warn("dvecSet 已弃用，请直接使用索引赋值", DeprecationWarning, stacklevel=2)
    v[i] = float(value)


def createOrder(values: Sequence[int] | np.ndarray) -> OrderObject:
    warnings.warn("createOrder 已弃用，请直接使用 OrderObject(data=...)", DeprecationWarning, stacklevel=2)
    if isinstance(values, np.ndarray):
        return OrderObject(data=values.astype(int).tolist())
    return OrderObject(data=[int(v) for v in values])


def setOrder(order: OrderObject, values: Sequence[int] | np.ndarray) -> None:
    warnings.warn("setOrder 已弃用，请直接使用 order.setFrom(...)", DeprecationWarning, stacklevel=2)
    if isinstance(values, np.ndarray):
        order.setFrom(values.astype(int).tolist())
    else:
        order.setFrom([int(v) for v in values])
