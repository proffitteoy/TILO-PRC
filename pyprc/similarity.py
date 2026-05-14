# 相似度矩阵构建
# 本模块提供高斯相似度和 KNN 相似度的稠密/稀疏矩阵构建函数。
from __future__ import annotations

import math
from typing import Tuple

import numpy as np

from .enums import GaussSimAdjMode, KNNAdjMode, PRCError
from .matrix import SparseAdjacencyData


def findAverageKNNDist(data: np.ndarray, k: int) -> float:
    """计算所有点到第 k 近邻的平均距离"""
    n = int(data.shape[0])
    if k <= 0 or k > n - 2:
        k = int(math.log(float(n)) + 1)
    avg = 0.0
    for i in range(n):
        diff = data - data[i]
        dist = np.sum(diff * diff, axis=1)
        nearest = np.partition(dist, k)[k]
        avg += math.sqrt(float(nearest))
    return avg / float(n)


def gaussSimMatrix(
    data: np.ndarray,
    sigma: float,
    mode: GaussSimAdjMode,
    eps: float = 1e-8,
    zero_diagonal: bool = True,
) -> Tuple[np.ndarray, float]:
    """构建稠密高斯相似度矩阵"""
    points = np.asarray(data, dtype=float)
    n = int(points.shape[0])
    if sigma <= 0:
        sigma = findAverageKNNDist(points, -1)
    result = points @ points.T
    g = -1.0 / (2.0 * sigma * sigma)
    for i in range(n):
        for j in range(i + 1, n):
            d = math.exp(g * (result[i, i] - 2.0 * result[i, j] + result[j, j]))
            if not (
                mode == GaussSimAdjMode.GS_ADJ_ALL
                or (mode == GaussSimAdjMode.GS_ADJ_THRESHOLD and d > eps)
            ):
                d = 0.0
            result[i, j] = d
            result[j, i] = d
        result[i, i] = 0.0 if zero_diagonal else 1.0
    return result, sigma


def gaussSimSparseMatrix(
    data: np.ndarray,
    sigma: float,
    mode: GaussSimAdjMode,
    eps: float = 1e-8,
    zero_diagonal: bool = True,
) -> Tuple[SparseAdjacencyData, float]:
    """构建稀疏高斯相似度矩阵"""
    points = np.asarray(data, dtype=float)
    n = int(points.shape[0])
    if sigma <= 0:
        sigma = findAverageKNNDist(points, -1)
    gamma = -1.0 / (2.0 * sigma * sigma)
    result = SparseAdjacencyData(n)
    for i in range(n):
        for j in range(i + 1, n):
            d = math.exp(float(np.sum((points[i] - points[j]) ** 2)) * gamma)
            if (mode == GaussSimAdjMode.GS_ADJ_ALL) or (
                mode == GaussSimAdjMode.GS_ADJ_THRESHOLD and d > eps
            ):
                result.add(i, j, d)
                result.add(j, i, d)
        if not zero_diagonal:
            result.add(i, i, 1.0)
    return result, sigma


def knnSimMatrix(
    data: np.ndarray,
    k: int,
    mode: KNNAdjMode,
    sigma: float = -1.0,
) -> Tuple[np.ndarray, int]:
    """构建稠密 KNN 相似度矩阵"""
    points = np.asarray(data, dtype=float)
    n = int(points.shape[0])
    if k <= 0:
        k = int(math.log(float(n)) + 1)
    if k + 1 >= n:
        raise PRCError("Invalid knn k value for data size.")
    if mode == KNNAdjMode.KNN_EITHER_ADJ_GAUSS and sigma <= 0:
        sigma = findAverageKNNDist(points, -1)
    gamma = -1.0 / (2.0 * sigma * sigma) if sigma > 0 else 0.0
    result = np.zeros((n, n), dtype=float)
    for i in range(n):
        diff = points - points[i]
        dist = np.sum(diff * diff, axis=1)
        idx = np.argsort(dist)[: k + 1]
        for j in idx:
            if int(j) == i:
                continue
            result[i, j] += 1.0
            result[j, i] += 0.25
    for i in range(n):
        for j in range(n):
            if result[i, j] <= 0:
                continue
            if mode == KNNAdjMode.KNN_EITHER_ADJ_ONE:
                result[i, j] = 1.0
                result[j, i] = 1.0
            elif mode == KNNAdjMode.KNN_BOTH_ADJ_ONE:
                result[i, j] = 1.0 if result[i, j] > 1.1 else 0.0
            elif mode == KNNAdjMode.KNN_BOTH_EITHER_ONE_ONEHALF:
                if result[i, j] > 1.1:
                    result[i, j] = 1.0
                elif result[i, j] > 0.1:
                    result[i, j] = 0.5
            elif mode == KNNAdjMode.KNN_EITHER_ADJ_GAUSS:
                d = math.exp(float(np.sum((points[i] - points[j]) ** 2)) * gamma)
                result[i, j] = d
                result[j, i] = d
            else:  # pragma: no cover
                raise PRCError("Unknown knn similarity mode.")
    return result, k


def knnSimSparseMatrix(
    data: np.ndarray,
    k: int,
    mode: KNNAdjMode,
    sigma: float = -1.0,
) -> Tuple[SparseAdjacencyData, int]:
    """构建稀疏 KNN 相似度矩阵"""
    points = np.asarray(data, dtype=float)
    n = int(points.shape[0])
    if k <= 0:
        k = int(math.log(float(n)) + 1)
    if k + 1 >= n:
        raise PRCError("Invalid knn k value for data size.")
    if mode == KNNAdjMode.KNN_EITHER_ADJ_GAUSS and sigma <= 0:
        sigma = findAverageKNNDist(points, -1)
    gamma = -1.0 / (2.0 * sigma * sigma) if sigma > 0 else 0.0

    result = SparseAdjacencyData(n)
    for i in range(n):
        diff = points - points[i]
        dist = np.sum(diff * diff, axis=1)
        idx = np.argsort(dist)[: k + 1]
        for j in idx:
            if int(j) == i:
                continue
            result.add(i, int(j), 1.0)
            result.add(int(j), i, 0.25)

    items = [(row, col, value) for row, bucket in enumerate(result.rows) for col, value in bucket.items()]
    for row, col, value in items:
        if value <= 0:
            continue
        if mode == KNNAdjMode.KNN_EITHER_ADJ_ONE:
            result.set(row, col, 1.0)
            result.set(col, row, 1.0)
        elif mode == KNNAdjMode.KNN_BOTH_ADJ_ONE:
            result.set(row, col, 1.0 if value > 1.1 else 0.0)
        elif mode == KNNAdjMode.KNN_BOTH_EITHER_ONE_ONEHALF:
            if value > 1.1:
                result.set(row, col, 1.0)
            elif value > 0.1:
                result.set(row, col, 0.5)
            else:
                result.set(row, col, 0.0)
        elif mode == KNNAdjMode.KNN_EITHER_ADJ_GAUSS:
            d = math.exp(float(np.sum((points[row] - points[col]) ** 2)) * gamma)
            result.set(row, col, d)
            result.set(col, row, d)
        else:  # pragma: no cover
            raise PRCError("Unknown knn similarity mode.")
    return result, k
