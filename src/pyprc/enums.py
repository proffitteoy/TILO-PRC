# 枚举类型与基础数据结构定义
# 本模块包含 PRC/TILO 算法使用的所有枚举类型、FlatStruct 数据类和自定义异常。
from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Sequence


class PRCError(RuntimeError):
    """PRC 算法专用异常"""
    pass


class KNNAdjMode(IntEnum):
    KNN_EITHER_ADJ_ONE = 0
    KNN_BOTH_ADJ_ONE = 1
    KNN_BOTH_EITHER_ONE_ONEHALF = 2
    KNN_EITHER_ADJ_GAUSS = 3


class GaussSimAdjMode(IntEnum):
    GS_ADJ_THRESHOLD = 0
    GS_ADJ_ALL = 1


class PrcMetricEnum(IntEnum):
    PinchRatio = 0
    RelRatio = 1
    CrossRatio = 2
    NCut = 3


class TagModeEnum(IntEnum):
    NO_TAGS = 0
    FRONT_TAGS = 1
    REAR_TAGS = -1


class FileStructureEnum(IntEnum):
    POINT_DATA = 0
    ADJACENCY_DATA = 1


class PointSimilarityEnum(IntEnum):
    UNDEFINED_ADJ_SIM = 0
    GAUSS_ADJ_SIM = 1
    KNN_ADJ_SIM = 2
    PRECALC_ADJ_SIM = 3


class FlatType(IntEnum):
    LocalMin = 0
    LocalMax = 1


@dataclass
class FlatStruct:
    start: int = 0
    stop: int = 0
    type: FlatType = FlatType.LocalMin

    def Print(self) -> str:
        kind = "min" if self.type == FlatType.LocalMin else "max"
        return f"{kind} {self.start} {self.stop}"


def PrintMarks(marks: Sequence[FlatStruct]) -> str:
    return ", ".join(mark.Print() for mark in marks)
