# 数据文件读取与评估工具
# 本模块提供文本矩阵、向量、METIS 格式图文件的读取函数，以及聚类纯度计算。
from __future__ import annotations

from pathlib import Path
from typing import List, Sequence, Tuple

import numpy as np

from .enums import PRCError, TagModeEnum
from .matrix import SparseAdjacencyData


def _strip_comment(line: str, comment_delimiter: str) -> str:
    if comment_delimiter:
        loc = line.find(comment_delimiter)
        if loc >= 0:
            return line[:loc]
    return line


def loadtxt_matrix(
    file_path: str | Path,
    comma_separated: bool = False,
    comment_delimiter: str = "#",
) -> np.ndarray:
    """从文本文件加载数值矩阵"""
    rows: List[List[float]] = []
    with open(file_path, "r", encoding="utf-8") as fin:
        for raw in fin:
            line = _strip_comment(raw.strip(), comment_delimiter).strip()
            if not line:
                continue
            if comma_separated:
                parts = [p.strip() for p in line.split(",") if p.strip()]
            else:
                parts = line.split()
            row = [float(x) for x in parts]
            if rows and len(row) != len(rows[0]):
                raise PRCError("Point data file has inconsistent row width.")
            rows.append(row)
    if not rows:
        raise PRCError("Point data file is empty.")
    return np.asarray(rows, dtype=float)


def loadtxt_vector_int(file_path: str | Path) -> np.ndarray:
    with open(file_path, "r", encoding="utf-8") as fin:
        values = [int(float(x)) for x in fin.read().split()]
    return np.asarray(values, dtype=int)


def loadtxt_vector_float(file_path: str | Path) -> np.ndarray:
    with open(file_path, "r", encoding="utf-8") as fin:
        values = [float(x) for x in fin.read().split()]
    return np.asarray(values, dtype=float)


def _parse_graph_header(header: str) -> Tuple[int, int, int, int]:
    parts = header.split()
    if len(parts) < 2:
        raise PRCError("Invalid graph header.")
    num_nodes = int(parts[0])
    num_edges = int(parts[1])
    fmt = int(parts[2]) if len(parts) >= 3 else 0
    ncon = int(parts[3]) if len(parts) >= 4 else 0
    return num_nodes, num_edges, fmt, ncon


def loadGraph(file_path: str | Path, node_offset: int) -> Tuple[np.ndarray, np.ndarray]:
    """从 METIS 格式文件加载稠密邻接矩阵"""
    with open(file_path, "r", encoding="utf-8") as fin:
        header = fin.readline()
        if not header:
            raise PRCError("Invalid graph file header.")
        num_nodes, _, fmt, ncon = _parse_graph_header(header)
        fmt_vsizes = fmt >= 100
        fmt_vweights = (fmt % 100) >= 10
        fmt_eweights = (fmt % 10) >= 1
        vw_size = 2 + max(0, ncon - 1)
        vertex_weights = np.ones((num_nodes, vw_size), dtype=float)
        result = np.zeros((num_nodes, num_nodes), dtype=float)
        count = 0
        for raw in fin:
            if count >= num_nodes:
                break
            parts = raw.split()
            if not parts:
                continue
            idx = 0
            wcount = 0
            if fmt_vsizes:
                vertex_weights[count, wcount] = float(parts[idx])
                idx += 1
                wcount += 1
            if fmt_vweights:
                for _ in range(max(1, ncon)):
                    vertex_weights[count, wcount] = float(parts[idx])
                    idx += 1
                    wcount += 1
            while idx < len(parts):
                tmp_node = int(parts[idx]) - node_offset
                idx += 1
                tmp_w = 1.0
                if fmt_eweights:
                    if idx >= len(parts):
                        raise PRCError("Invalid weighted adjacency line.")
                    tmp_w = float(parts[idx])
                    idx += 1
                if tmp_node >= num_nodes:
                    raise PRCError("node id out of range")
                result[count, tmp_node] = tmp_w
            count += 1
    return result, vertex_weights


def loadSparseGraph(file_path: str | Path, node_offset: int) -> Tuple[SparseAdjacencyData, np.ndarray]:
    """从 METIS 格式文件加载稀疏邻接矩阵"""
    with open(file_path, "r", encoding="utf-8") as fin:
        header = fin.readline()
        if not header:
            raise PRCError("Invalid graph file header.")
        num_nodes, _, fmt, ncon = _parse_graph_header(header)
        fmt_vsizes = fmt >= 100
        fmt_vweights = (fmt % 100) >= 10
        fmt_eweights = (fmt % 10) >= 1
        vw_size = 2 + max(0, ncon - 1)
        vertex_weights = np.ones((num_nodes, vw_size), dtype=float)
        result = SparseAdjacencyData(num_nodes)
        count = 0
        for raw in fin:
            if count >= num_nodes:
                break
            parts = raw.split()
            if not parts:
                continue
            idx = 0
            wcount = 0
            if fmt_vsizes:
                vertex_weights[count, wcount] = float(parts[idx])
                idx += 1
                wcount += 1
            if fmt_vweights:
                for _ in range(max(1, ncon)):
                    vertex_weights[count, wcount] = float(parts[idx])
                    idx += 1
                    wcount += 1
            while idx < len(parts):
                tmp_node = int(parts[idx]) - node_offset
                idx += 1
                tmp_w = 1.0
                if fmt_eweights:
                    if idx >= len(parts):
                        raise PRCError("Invalid weighted adjacency line.")
                    tmp_w = float(parts[idx])
                    idx += 1
                if tmp_node > num_nodes:
                    raise PRCError("node id out of range")
                result.add(count, tmp_node, tmp_w)
            count += 1
    return result, vertex_weights


def _slice_tags(data: np.ndarray, mode: TagModeEnum) -> np.ndarray:
    """根据标签位置模式去除标签列"""
    if mode == TagModeEnum.NO_TAGS:
        return data
    if mode == TagModeEnum.FRONT_TAGS:
        return data[:, 1:]
    if mode == TagModeEnum.REAR_TAGS:
        return data[:, :-1]
    raise PRCError("Unknown tag mode.")


def calcPurity(pred_labels: Sequence[int], true_labels: Sequence[int]) -> float:
    """计算聚类纯度"""
    if len(pred_labels) != len(true_labels):
        raise PRCError("pred_labels and true_labels must have same length.")
    class_map: dict[int, dict[int, int]] = {}
    for p, t in zip(pred_labels, true_labels):
        sub = class_map.setdefault(int(p), {})
        sub[int(t)] = sub.get(int(t), 0) + 1
    max_count_sum = 0
    for sub in class_map.values():
        if sub:
            max_count_sum += max(sub.values())
    return float(max_count_sum) / float(len(pred_labels)) if pred_labels else 0.0
