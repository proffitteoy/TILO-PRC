# PRC/TILO 纯 Python 实现的包初始化
# 本模块导出所有公开 API，供 import pyprc 使用。

from .enums import (
    FileStructureEnum,
    FlatStruct,
    FlatType,
    GaussSimAdjMode,
    KNNAdjMode,
    PointSimilarityEnum,
    PRCError,
    PrcMetricEnum,
    PrintMarks,
    TagModeEnum,
)
from .structs import (
    AdjDataConfigStruct,
    DataConfigStruct,
    GaussAdjPolicyStruct,
    KnnAdjPolicyStruct,
    PointDataConfigStruct,
    PrcCountsStruct,
    PrcMetricValues,
    PrcPolicyStruct,
    PrcReturnStruct,
    RunConfigStruct,
    TiloPolicyStruct,
)
from .rng import _GLOBAL_C_RAND, _cpp_shuffle_values
from .matrix import (
    BoundaryObject,
    MatrixStorage,
    SparseAdjacencyData,
    _to_square_numpy_matrix,
)
from .order import OrderObject, VirtualOrderObject
from .similarity import (
    findAverageKNNDist,
    gaussSimMatrix,
    gaussSimSparseMatrix,
    knnSimMatrix,
    knnSimSparseMatrix,
)
from .io import (
    calcPurity,
    loadGraph,
    loadSparseGraph,
    loadtxt_matrix,
    loadtxt_vector_float,
    loadtxt_vector_int,
)
from .algorithm import (
    TILO,
    RefineTILO,
    calcBoundaries,
    calcBoundariesFromMatrix,
    cless,
    findSplitLocation,
    initOrder_from_files,
    initOrder_random,
    pinchRatioClustering,
    pinchRatioClustering_storage,
)
from .cli import (
    process_cmd_line,
    readData,
    run_gen_sim_matrix_cli,
    run_pinch_ratio_clustering_cli,
)
from .compat import (
    createOrder,
    dvec,
    dvecAt,
    dvecSet,
    ivec,
    ivecAt,
    ivecSet,
    setOrder,
    sparse_TILO,
    sparse_calcBoundaries,
    sparse_pinchRatioClustering,
)

__all__ = [name for name in globals() if not name.startswith("_")]
