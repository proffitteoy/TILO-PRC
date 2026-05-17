# TILO/PRC 核心算法
# 本模块实现边界计算、TILO 位移操作、切分点查找和 PRC 递归二分聚类。
from __future__ import annotations

import heapq
import math
from dataclasses import dataclass
from typing import List, MutableSequence, Sequence, Tuple

import numpy as np

from .enums import FlatStruct, FlatType, PRCError, PrcMetricEnum, PrintMarks
from .matrix import BoundaryObject, MatrixStorage, _to_square_numpy_matrix
from .order import OrderObject, VirtualOrderObject
from .rng import _GLOBAL_C_RAND, _cpp_random_shuffle
from .structs import (
    PrcCountsStruct,
    PrcMetricValues,
    PrcPolicyStruct,
    PrcReturnStruct,
    TiloPolicyStruct,
)


def _calc_boundaries_internal(boundary: BoundaryObject, matrix: MatrixStorage, order: OrderObject) -> None:
    boundary.resize(order.size(), order.getPrefixDegree(matrix))
    for i in range(boundary.size()):
        boundary.set_at(i, order.slope(i - 1, i, matrix) + boundary.at(i - 1))


def calcBoundaries(
    arg1: BoundaryObject | object,
    arg2: MatrixStorage | OrderObject,
    arg3: OrderObject | None = None,
) -> None:
    """计算边界值序列（支持内部和公开两种调用方式）"""
    if isinstance(arg1, BoundaryObject) and isinstance(arg2, MatrixStorage) and isinstance(arg3, OrderObject):
        _calc_boundaries_internal(arg1, arg2, arg3)
        return
    if arg3 is not None:
        raise PRCError("Invalid calcBoundaries call signature.")
    matrix = MatrixStorage(_to_square_numpy_matrix(arg1))
    if not isinstance(arg2, OrderObject):
        raise PRCError("calcBoundaries(matrix, order) expects an OrderObject.")
    _calc_boundaries_internal(arg2.boundary(), matrix, arg2)
    arg2.boundary().findLocalMinAndMax(arg2.marks())


def doShifts(
    marks: Sequence[FlatStruct],
    order: OrderObject,
    boundary: BoundaryObject,
    matrix: MatrixStorage,
    epsilon: float,
) -> Tuple[int, int]:
    """TILO 标准位移操作：对每个局部最大值搜索可降低峰值的节点"""
    count = 0
    inversion_count = 0
    prev_s = -1
    for z, mark in enumerate(marks):
        if mark.type == FlatType.LocalMin:
            continue
        y = 0
        i = mark.start
        upper_limit = order.size() - 1
        if i >= upper_limit:
            i = upper_limit - 1
        if i < 0:
            continue
        j = mark.stop
        prev_min = -1
        next_min = boundary.size() - 1
        if z > 0:
            prev_min = marks[z - 1].stop
        if z + 1 < len(marks):
            next_min = marks[z + 1].start
        s_ai = boundary.at(i + 1) - boundary.at(i)
        s_bj = boundary.at(j) - boundary.at(j - 1)
        yval = epsilon * (1.0 + abs(s_ai))
        ytmp = epsilon
        eps_sqrt = math.sqrt(epsilon)
        orig_yval = yval
        for k in range(prev_min + 1, i + 1):
            tmp = order.slope(i, k, matrix)
            tmp2 = tmp - s_ai - 2.0 * matrix.getCoeff(order.at(k), order.at(i + 1))
            if ((tmp > ytmp) and (tmp2 > yval)) or (
                (tmp > ytmp) and (ytmp < eps_sqrt) and (tmp2 > orig_yval)
            ):
                y = k
                ytmp = abs(tmp)
                yval = tmp2

        for k in range(j + 1, min(next_min, upper_limit) + 1):
            tmp = order.slope(j, k, matrix)
            tmp2 = -tmp + s_bj - 2.0 * matrix.getCoeff(order.at(k), order.at(j))
            if ((tmp < -ytmp) and (tmp2 > yval)) or (
                (tmp < -ytmp) and (ytmp < eps_sqrt) and (tmp2 > orig_yval)
            ):
                y = k
                ytmp = abs(tmp)
                yval = tmp2

        if yval > orig_yval:
            if y <= i:
                if y == prev_s:
                    continue
                prev_s = i + 1
                order.applyShift(y, i + 1, matrix)
                count += 1
                inversion_count += i + 1 - y
            else:
                if y > upper_limit:
                    continue
                if j == prev_s:
                    continue
                prev_s = y
                order.applyShift(y, j, matrix)
                count += 1
                inversion_count += y - j
    return count, inversion_count


def doRShifts(
    marks: Sequence[FlatStruct],
    order: OrderObject,
    boundary: BoundaryObject,
    matrix: MatrixStorage,
    epsilon: float,
) -> Tuple[int, int]:
    """TILO 精细位移操作：在局部最大值附近更大范围搜索"""
    count = 0
    inversion_count = 0
    prev_s = -1
    for z, mark in enumerate(marks):
        if mark.type == FlatType.LocalMin:
            continue
        y = 0
        mx_i = mark.start
        mx_j = mark.stop
        prev_min = -1
        next_min = boundary.size() - 1
        if z > 0:
            prev_min = marks[z - 1].stop
        if z + 1 < len(marks):
            next_min = marks[z + 1].start
        mx_s_ai = boundary.at(mx_i + 1) - boundary.at(mx_i) if (mx_i + 1) < boundary.size() else -boundary.at(mx_i)
        yval = epsilon * (1.0 + abs(mx_s_ai))
        ytmp = epsilon
        eps_sqrt = math.sqrt(epsilon)
        orig_yval = yval
        r = mx_i
        upper_limit = order.size() - 1

        for i in range(mx_i, prev_min, -1):
            if i + 1 > upper_limit:
                continue
            s_ai = boundary.at(i + 1) - boundary.at(i) if (i + 1) < boundary.size() else -boundary.at(i)
            for k in range(prev_min + 1, i + 1):
                tmp = order.slope(i, k, matrix)
                tmp2 = tmp - s_ai - 2.0 * matrix.getCoeff(order.at(k), order.at(i + 1))
                if ((tmp > ytmp) and (tmp2 > yval)) or (
                    (tmp > ytmp) and (ytmp < eps_sqrt) and (tmp2 > orig_yval)
                ):
                    y = k
                    r = i
                    ytmp = abs(tmp)
                    yval = tmp2
            if yval > orig_yval:
                break

        for j in range(mx_j, next_min + 1):
            if yval > orig_yval:
                break
            s_bj = boundary.at(j) - boundary.at(j - 1)
            for k in range(j + 1, min(next_min, upper_limit) + 1):
                tmp = order.slope(j, k, matrix)
                tmp2 = -tmp + s_bj - 2.0 * matrix.getCoeff(order.at(k), order.at(j))
                if ((tmp < -ytmp) and (tmp2 > yval)) or (
                    (tmp < -ytmp) and (ytmp < eps_sqrt) and (tmp2 > orig_yval)
                ):
                    y = k
                    r = j
                    ytmp = abs(tmp)
                    yval = tmp2

        if yval > orig_yval:
            if y <= mx_i:
                if (r + 1) > upper_limit:
                    continue
                if y == prev_s:
                    continue
                prev_s = r + 1
                order.applyShift(y, r + 1, matrix)
                count += 1
                inversion_count += r + 1 - y
            else:
                if y > upper_limit:
                    continue
                if r == prev_s:
                    continue
                prev_s = y
                order.applyShift(y, r, matrix)
                count += 1
                inversion_count += y - r
    return count, inversion_count


# --- PLACEHOLDER_TILO ---


def _TILO_internal(order: OrderObject, matrix: MatrixStorage, policy: TiloPolicyStruct | None = None) -> PrcCountsStruct:
    policy = policy or TiloPolicyStruct()
    loop_count = 0
    flag = 1
    shift_count = 0
    inversion_count = 0
    while flag > 0 and loop_count < policy.maxIterations:
        shifts, inversions = order.updateOrder(matrix, policy.tiloEpsilon)
        flag = shifts
        shift_count += shifts
        inversion_count += inversions
        loop_count += 1
    if loop_count >= policy.maxIterations:
        raise PRCError("Reached max iteration limit in TILO")
    return PrcCountsStruct(shift_count, inversion_count, loop_count)


def _RefineTILO_internal(
    order: OrderObject, matrix: MatrixStorage, policy: TiloPolicyStruct | None = None
) -> PrcCountsStruct:
    policy = policy or TiloPolicyStruct()
    loop_count = 0
    flag = 1
    shift_count = 0
    inversion_count = 0
    while flag > 0 and loop_count < policy.maxIterations:
        shifts, inversions = order.refineOrder(matrix, policy.tiloEpsilon)
        flag = shifts
        shift_count += shifts
        inversion_count += inversions
        loop_count += 1
    if loop_count >= policy.maxIterations:
        raise PRCError("Reached max iteration limit in RefineTILO")
    return PrcCountsStruct(shift_count, inversion_count, loop_count)


def TILO(
    arg1: OrderObject | object,
    arg2: MatrixStorage | OrderObject,
    arg3: TiloPolicyStruct | None = None,
) -> PrcCountsStruct:
    """运行 TILO 排序算法（支持内部和公开两种调用方式）"""
    if isinstance(arg1, OrderObject) and isinstance(arg2, MatrixStorage):
        return _TILO_internal(arg1, arg2, arg3)
    matrix = MatrixStorage(_to_square_numpy_matrix(arg1))
    if not isinstance(arg2, OrderObject):
        raise PRCError("TILO(matrix, order) expects an OrderObject.")
    return _TILO_internal(arg2, matrix, arg3)


def RefineTILO(
    arg1: OrderObject | object,
    arg2: MatrixStorage | OrderObject,
    arg3: TiloPolicyStruct | None = None,
) -> PrcCountsStruct:
    """运行精细 TILO 排序算法"""
    if isinstance(arg1, OrderObject) and isinstance(arg2, MatrixStorage):
        return _RefineTILO_internal(arg1, arg2, arg3)
    matrix = MatrixStorage(_to_square_numpy_matrix(arg1))
    if not isinstance(arg2, OrderObject):
        raise PRCError("RefineTILO(matrix, order) expects an OrderObject.")
    return _RefineTILO_internal(arg2, matrix, arg3)


# --- PLACEHOLDER_SPLIT ---


def _find_split_location_internal(
    cur_order: OrderObject,
    matrix: MatrixStorage,
    vorder: OrderObject,
    metric: PrcMetricEnum,
    eval_all_metrics: bool = False,
) -> Tuple[PrcMetricValues, int, float]:
    """在边界曲线上查找最佳切分点"""
    results = PrcMetricValues()
    best_r = float("inf")
    best_d = -float("inf")
    best_index = -1
    cur_start = cur_order.baseStart() - vorder.baseStart()
    cur_stop = cur_order.baseStart() + cur_order.size() - 1 - vorder.baseStart()
    marks = vorder.marks()
    boundary = vorder.boundary()
    for z, mark in enumerate(marks):
        if mark.type == FlatType.LocalMax:
            continue
        if mark.start >= cur_stop:
            continue
        if mark.stop <= cur_start:
            continue
        if mark.start == cur_start:
            continue
        local_min_cut = boundary.at(mark.start)
        am = local_min_cut
        ax = z
        for x in range(z - 1, -1, -1):
            if marks[x].start <= cur_start:
                break
            if marks[x].type == FlatType.LocalMin:
                continue
            bval = boundary.at(marks[x].start)
            if bval > am:
                am = bval
                ax = x
        bm = local_min_cut
        bx = z
        for x in range(z + 1, len(marks)):
            if marks[x].start >= cur_stop:
                break
            if marks[x].type == FlatType.LocalMin:
                continue
            bval = boundary.at(marks[x].start)
            if bval > bm:
                bm = bval
                bx = x
        thickwidth_both = min(am, bm)
        diff_minmax = thickwidth_both - local_min_cut
        d_a = 0.0
        d_b = 0.0
        a_int = 0.0
        b_int = 0.0
        a2_ext = 0.0
        b2_ext = 0.0
        rel_b = float("inf")
        rel_a = float("inf")
        pinch_r = abs(local_min_cut / thickwidth_both) if thickwidth_both > 0 else float("inf")
        ncut_v = float("inf")
        cross_r = float("inf")
        r_ratio = float("inf")

        if eval_all_metrics or metric == PrcMetricEnum.NCut:
            for ttt in range(cur_start, marks[z].start + 1):
                d_a += matrix.degree(vorder.at(ttt))
            for ttt in range(marks[z].start + 1, cur_stop + 1):
                d_b += matrix.degree(vorder.at(ttt))
            ncut_v = (local_min_cut / d_a + local_min_cut / d_b) if (d_a > 0 and d_b > 0) else float("inf")

        if eval_all_metrics or metric in {PrcMetricEnum.CrossRatio, PrcMetricEnum.RelRatio}:
            a_int, a2_ext, b_int, b2_ext = matrix.calcCuts(
                cur_start,
                marks[ax].start,
                marks[z].start,
                marks[bx].start,
                cur_stop,
                vorder,
            )
            rel_b = (b2_ext / b_int) if b_int > 0 else float("inf")
            rel_a = (a2_ext / a_int) if a_int > 0 else float("inf")
            cross_r = (rel_a * rel_b) if (a_int > 0 and b_int > 0) else float("inf")
            r_ratio = min(rel_a, rel_b)

        if metric == PrcMetricEnum.PinchRatio:
            quality = pinch_r
        elif metric == PrcMetricEnum.NCut:
            quality = ncut_v
        elif metric == PrcMetricEnum.CrossRatio:
            quality = cross_r
        elif metric == PrcMetricEnum.RelRatio:
            quality = r_ratio
        else:  # pragma: no cover
            raise PRCError("invalid metric in pinch ratio split")

        if (quality < best_r) or ((quality == best_r) and (diff_minmax > best_d)):
            best_r = quality
            best_d = diff_minmax
            best_index = z
            results.mincut = local_min_cut
            results.minmaxcutA = am
            results.minmaxcutB = bm
            results.intA = a_int
            results.extA = a2_ext
            results.intB = b_int
            results.extB = b2_ext
            results.dA = d_a
            results.dB = d_b
            results.pinchRatio = pinch_r
            results.ncut = ncut_v
            results.relA = rel_a
            results.relB = rel_b
            results.relRatio = r_ratio
            results.crossRatio = cross_r

    value = best_r
    results.loc = -1
    if best_index >= 0:
        loc = marks[best_index].start - cur_start
        results.loc = marks[best_index].start
    else:
        loc = -1
    return results, loc, value


def findSplitLocation(
    matrix_like: object,
    order: OrderObject,
    metric: PrcMetricEnum,
    eval_all_metrics: bool = False,
) -> Tuple[float, int, PrcMetricValues]:
    matrix = MatrixStorage(_to_square_numpy_matrix(matrix_like))
    calcBoundaries(order.boundary(), matrix, order)
    order.boundary().findLocalMinAndMax(order.marks())
    mvalues, loc, value = _find_split_location_internal(order, matrix, order, metric, eval_all_metrics)
    return value, loc, mvalues


# --- PLACEHOLDER_PRC ---


@dataclass
class _PQStruct:
    quality: float
    loc: int
    order: OrderObject
    mvalues: PrcMetricValues


def pinchRatioClustering_storage(
    matrix: MatrixStorage,
    order: OrderObject,
    k: int,
    policy: PrcPolicyStruct,
) -> Tuple[PrcReturnStruct, np.ndarray]:
    """PRC 核心算法：基于优先队列的递归二分聚类"""
    if matrix.rows() != matrix.cols():
        raise PRCError("Adjacency matrix must be square.")
    if k <= 1:
        raise PRCError("numberOfPartitions must be >= 2")
    n = matrix.rows()
    if order.size() < n:
        raise PRCError("Invalid Order Object. Not large enough for matrix A.")

    count_totals = PrcCountsStruct()
    return_results = PrcReturnStruct()

    tmp_counts = TILO(order, matrix, policy.tiloPolicy)
    count_totals.add(tmp_counts)
    if policy.prcRefineTILO:
        tmp_counts = RefineTILO(order, matrix, policy.tiloPolicy)
        count_totals.add(tmp_counts)

    return_ro = policy.prcRecurseTILO and policy.prcReturnRecursiveOrder
    tmp_order = order.clone() if not return_ro else None
    rvorder = VirtualOrderObject(order if return_ro else tmp_order)  # type: ignore[arg-type]
    rvorder.b = order.b.clone()
    rvorder.m = [FlatStruct(m.start, m.stop, m.type) for m in order.m]

    heap: List[Tuple[float, int, _PQStruct]] = []
    heap_counter = 0

    def push_item(item: _PQStruct) -> None:
        nonlocal heap_counter
        heapq.heappush(heap, (-item.quality, heap_counter, item))
        heap_counter += 1

    def peek_item() -> _PQStruct:
        return heap[0][2]

    def pop_item() -> _PQStruct:
        return heapq.heappop(heap)[2]

    if policy.prcRecurseTILO:
        mvals, loc, value = _find_split_location_internal(rvorder, matrix, rvorder, policy.metric, policy.prcEvalAllMetrics)
        push_item(_PQStruct(-value, loc, rvorder, mvals))
        while len(heap) < k:
            cur = peek_item()
            if cur.quality > 0 or cur.loc < 0:
                break
            pop_item()
            return_results.mvalues.append(cur.mvalues)
            tmp_a, tmp_b = cur.order.split(cur.loc, reverse_b=policy.reverseOrderOnSplit)

            tmp_counts = TILO(tmp_a, matrix, policy.tiloPolicy)
            count_totals.add(tmp_counts)
            if policy.prcRefineTILO:
                tmp_counts = RefineTILO(tmp_a, matrix, policy.tiloPolicy)
                count_totals.add(tmp_counts)
            mv_a, loc_a, val_a = _find_split_location_internal(
                tmp_a, matrix, tmp_a, policy.metric, policy.prcEvalAllMetrics
            )
            push_item(_PQStruct(-val_a, loc_a, tmp_a, mv_a))

            tmp_counts = TILO(tmp_b, matrix, policy.tiloPolicy)
            count_totals.add(tmp_counts)
            if policy.prcRefineTILO:
                tmp_counts = RefineTILO(tmp_b, matrix, policy.tiloPolicy)
                count_totals.add(tmp_counts)
            mv_b, loc_b, val_b = _find_split_location_internal(
                tmp_b, matrix, tmp_b, policy.metric, policy.prcEvalAllMetrics
            )
            push_item(_PQStruct(-val_b, loc_b, tmp_b, mv_b))
    else:
        mvals, loc, value = _find_split_location_internal(rvorder, matrix, order, policy.metric, policy.prcEvalAllMetrics)
        push_item(_PQStruct(-value, loc, rvorder, mvals))
        while len(heap) < k:
            cur = peek_item()
            if cur.quality > 0 or cur.loc < 0:
                break
            pop_item()
            return_results.mvalues.append(cur.mvalues)
            tmp_a, tmp_b = cur.order.split(cur.loc, reverse_b=False)
            mv_a, loc_a, val_a = _find_split_location_internal(
                tmp_a, matrix, order, policy.metric, policy.prcEvalAllMetrics
            )
            tmp_a.b.resize(0, 0.0)
            tmp_a.m.clear()
            push_item(_PQStruct(-val_a, loc_a, tmp_a, mv_a))

            mv_b, loc_b, val_b = _find_split_location_internal(
                tmp_b, matrix, order, policy.metric, policy.prcEvalAllMetrics
            )
            tmp_b.b.resize(0, 0.0)
            tmp_b.m.clear()
            push_item(_PQStruct(-val_b, loc_b, tmp_b, mv_b))

    labels = np.full(n, -1, dtype=int)
    tag = 0
    while heap:
        cur = pop_item()
        for idx in range(cur.order.size()):
            labels[cur.order.at(idx)] = tag
        if return_ro:
            s = cur.order.baseStart()
            for idx, val in enumerate(cur.order.b.data()):
                if 0 <= s + idx < order.b.size():
                    order.b.b[s + idx] = float(val)
        tag += 1

    return_results.counts = count_totals
    return return_results, labels


def _copy_order_back(target: object, order: OrderObject) -> None:
    if isinstance(target, OrderObject):
        target.setFrom(order.vdata)
        target.b = order.b.clone()
        target.m = [FlatStruct(m.start, m.stop, m.type) for m in order.m]
        return
    if isinstance(target, np.ndarray):
        if target.shape[0] != order.size():
            raise PRCError("order vector size mismatch.")
        target[:] = np.asarray(order.vdata, dtype=target.dtype)
        return
    if isinstance(target, MutableSequence):
        if len(target) != order.size():
            raise PRCError("order sequence size mismatch.")
        for i, value in enumerate(order.vdata):
            target[i] = value
        return
    raise PRCError("Unsupported order object type.")


def _copy_labels_back(target: object, labels: np.ndarray) -> None:
    if isinstance(target, np.ndarray):
        if target.shape[0] != labels.shape[0]:
            raise PRCError("labels vector size mismatch.")
        target[:] = labels.astype(target.dtype)
        return
    if isinstance(target, MutableSequence):
        if len(target) != labels.shape[0]:
            raise PRCError("labels sequence size mismatch.")
        for i, value in enumerate(labels.tolist()):
            target[i] = int(value)
        return
    raise PRCError("Unsupported labels object type.")


def pinchRatioClustering(
    matrix_like: object,
    order_like: OrderObject | MutableSequence[int] | np.ndarray,
    labels_like: MutableSequence[int] | np.ndarray,
    k: int,
    policy: PrcPolicyStruct,
) -> PrcReturnStruct:
    """PRC 聚类公开入口"""
    matrix = MatrixStorage(_to_square_numpy_matrix(matrix_like))
    n = matrix.rows()
    if isinstance(order_like, OrderObject):
        order = order_like.clone()
    else:
        values = list(int(x) for x in list(order_like))
        if len(values) == 0:
            values = _cpp_random_shuffle(range(n), _GLOBAL_C_RAND.rand)
        order = OrderObject(data=values)
    result, labels = pinchRatioClustering_storage(matrix, order, k, policy)
    _copy_order_back(order_like, order)
    _copy_labels_back(labels_like, labels)
    return result


def calcBoundariesFromMatrix(matrix_like: object, order_like: OrderObject) -> None:
    matrix = MatrixStorage(_to_square_numpy_matrix(matrix_like))
    calcBoundaries(order_like.boundary(), matrix, order_like)
    order_like.boundary().findLocalMinAndMax(order_like.marks())


def _validate_order_vector(order_vec: Sequence[int], n: int) -> None:
    if len(order_vec) != n:
        raise PRCError(f"Initial order file size differs from data file: {len(order_vec)} vs {n}")
    seen = [0] * n
    for value in order_vec:
        if value < 0 or value >= n:
            raise PRCError("ERROR: order indexing out of range.")
        seen[value] += 1
    for idx, count in enumerate(seen):
        if count == 0:
            raise PRCError(f"Error: order missed location {idx}")
        if count > 1:
            raise PRCError(f"Error: order duplicated location {idx}")


def initOrder_random(n: int) -> OrderObject:
    return OrderObject(data=_cpp_random_shuffle(range(n), _GLOBAL_C_RAND.rand))


def initOrder_from_files(
    n: int,
    run_config: object,
) -> Tuple[bool, OrderObject]:
    from .io import loadtxt_vector_float, loadtxt_vector_int
    if run_config.initOrderFile:
        order_vec = loadtxt_vector_int(run_config.initOrderFile).tolist()
        _validate_order_vector(order_vec, n)
        return True, OrderObject(data=order_vec)

    if run_config.initLabelsFile:
        labels = loadtxt_vector_float(run_config.initLabelsFile).astype(int)
        if labels.shape[0] != n:
            raise PRCError(f"Initial label file size differs from data file: {labels.shape[0]} vs {n}")
        bucket: dict[int, List[int]] = {}
        for i, lbl in enumerate(labels.tolist()):
            bucket.setdefault(int(lbl), []).append(i)
        order_vec_list: List[int] = []
        for key in sorted(bucket.keys()):
            order_vec_list.extend(bucket[key])
        _validate_order_vector(order_vec_list, n)
        return True, OrderObject(data=order_vec_list)

    return False, initOrder_random(n)


def cless(
    a: PrcReturnStruct,
    b: PrcReturnStruct,
    a_boundary: Sequence[float],
    b_boundary: Sequence[float],
) -> bool:
    """比较两次 PRC 结果，返回 a 是否优于 b"""
    cureps = 1e-12
    for av, bv in zip(a_boundary, b_boundary):
        if (av - bv) < (-1.0 * cureps * (1.0 + bv)):
            return True
        if (av - bv) > (1.0 * cureps * (1.0 + bv)):
            return False

    if abs(a.averageWeightedClusterQuality - b.averageWeightedClusterQuality) > 1e-10:
        return a.averageWeightedClusterQuality < b.averageWeightedClusterQuality
    if abs(a.averageClusterQuality - b.averageClusterQuality) > 1e-10:
        return a.averageClusterQuality < b.averageClusterQuality
    if abs(a.weightedGeometricMean - b.weightedGeometricMean) > 1e-10:
        return a.weightedGeometricMean < b.weightedGeometricMean
    if abs(a.geometricMean - b.geometricMean) > 1e-10:
        return a.geometricMean < b.geometricMean
    return False
