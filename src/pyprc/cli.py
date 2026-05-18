# 命令行接口
# 本模块提供命令行参数解析、数据读取编排和两个 CLI 入口函数。
from __future__ import annotations

import time
from typing import List, Sequence, Tuple

import numpy as np

from .enums import (
    FileStructureEnum,
    GaussSimAdjMode,
    KNNAdjMode,
    PointSimilarityEnum,
    PRCError,
    PrcMetricEnum,
    PrintMarks,
    TagModeEnum,
)
from .matrix import MatrixStorage
from .order import OrderObject
from .rng import _GLOBAL_C_RAND
from .structs import (
    DataConfigStruct,
    GaussAdjPolicyStruct,
    KnnAdjPolicyStruct,
    PrcPolicyStruct,
    PrcReturnStruct,
    RunConfigStruct,
)
from .algorithm import (
    calcBoundariesFromMatrix,
    cless,
    initOrder_from_files,
    initOrder_random,
    pinchRatioClustering_storage,
)
from .io import (
    _slice_tags,
    calcPurity,
    loadGraph,
    loadSparseGraph,
    loadtxt_matrix,
)
from .pipeline import GraphBuildConfig, build_similarity_matrix_from_points


def _as_bool(raw_value: str, opt_name: str) -> bool:
    token = raw_value.strip().lower()
    if token in {"1", "true", "yes", "on"}:
        return True
    if token in {"0", "false", "no", "off"}:
        return False
    raise PRCError(f"Failed to convert {raw_value} into boolean for option --{opt_name}.")


def _require_value(argv: Sequence[str], i: int, opt_name: str) -> str:
    if i + 1 >= len(argv):
        raise PRCError(f"Missing value for option --{opt_name}")
    return argv[i + 1]


def process_cmd_line(
    argv: Sequence[str],
    policy: PrcPolicyStruct,
    knn_policy: KnnAdjPolicyStruct,
    gauss_policy: GaussAdjPolicyStruct,
    run_config: RunConfigStruct,
    data_config: DataConfigStruct,
    gen_sim_mode: bool = False,
) -> Tuple[bool, str]:
    """解析命令行参数，填充各配置结构体"""
    print_usage = False
    output_file_name = "simMatrix.txt"
    i = 0
    while i < len(argv):
        arg = argv[i]
        if not arg.startswith("--"):
            if not data_config.inputFileName:
                data_config.inputFileName = arg
            elif gen_sim_mode:
                output_file_name = arg
            else:
                try:
                    run_config.numberOfPartitions = int(arg)
                except ValueError:
                    raise PRCError(
                        f"Failed to convert {arg} into an integer number of partitions."
                    )
                if run_config.numberOfPartitions < 2:
                    raise PRCError(
                        f"Invalid number of partitions : {run_config.numberOfPartitions}. Must be >= 2."
                    )
            i += 1
            continue

        opt = arg[2:]
        if opt == "seed":
            run_config.seed = max(0, int(_require_value(argv, i, opt)))
            i += 2
        elif opt == "numpart":
            value = int(_require_value(argv, i, opt))
            if value < 2:
                raise PRCError(f"Invalid number of partitions : {value}")
            run_config.numberOfPartitions = value
            i += 2
        elif opt == "verbose":
            run_config.verboseLevel = int(_require_value(argv, i, opt))
            i += 2
        elif opt == "useTransduction":
            run_config.useTransduction = _as_bool(_require_value(argv, i, opt), opt)
            if run_config.useTransduction:
                run_config.useTransduction = False
            i += 2
        elif opt == "saveOrder":
            run_config.saveOrder = _as_bool(_require_value(argv, i, opt), opt)
            i += 2
        elif opt == "saveLabels":
            run_config.saveLabels = _as_bool(_require_value(argv, i, opt), opt)
            i += 2
        elif opt == "seedSuffixFlag":
            run_config.seedSuffix = _as_bool(_require_value(argv, i, opt), opt)
            i += 2
        elif opt == "outputLabelSuffix":
            run_config.outputLabelSuffix = _require_value(argv, i, opt)
            i += 2
        elif opt == "outputOrderSuffix":
            run_config.outputOrderSuffix = _require_value(argv, i, opt)
            i += 2
        elif opt == "infoSuffix":
            run_config.infoSuffix = _require_value(argv, i, opt)
            i += 2
        elif opt == "useMultiLevelPRC":
            run_config.useMultiLevelPRC = _as_bool(_require_value(argv, i, opt), opt)
            i += 2
        elif opt == "initOrderFile":
            run_config.initOrderFile = _require_value(argv, i, opt)
            i += 2
        elif opt == "initLabelsFile":
            run_config.initLabelsFile = _require_value(argv, i, opt)
            i += 2
        elif opt == "numInitOrderings":
            value = int(_require_value(argv, i, opt))
            if value <= 0:
                raise PRCError(f"Invalid number initial orderings : {value}")
            run_config.numberInitOrderings = value
            i += 2
        elif opt == "saveMultipleRuns":
            run_config.saveMultipleRuns = _as_bool(_require_value(argv, i, opt), opt)
            i += 2
        elif opt == "dataInput":
            data_config.inputFileName = _require_value(argv, i, opt)
            i += 2
        elif opt == "fileType":
            value = int(_require_value(argv, i, opt))
            if value not in {0, 1}:
                raise PRCError(f"Invalid file type value : {value}")
            data_config.fileType = FileStructureEnum(value)
            i += 2
        elif opt == "useSparseMatrix":
            data_config.useSparseMatrix = _as_bool(_require_value(argv, i, opt), opt)
            i += 2
        elif opt == "commaSeparated":
            data_config.commaSeparated = _as_bool(_require_value(argv, i, opt), opt)
            i += 2
        elif opt in {"commentDelimeter", "commentDelimiter"}:
            data_config.commentDelimiter = _require_value(argv, i, opt)
            i += 2
        elif opt == "tagLoc":
            value = int(_require_value(argv, i, opt))
            if value not in {0, 1, -1}:
                raise PRCError(f"Invalid Tag location : {value}, expected 0,1,or -1.")
            data_config.pointDataConfig.tagLoc = TagModeEnum(value)
            i += 2
        elif opt == "pointSimilarity":
            value = int(_require_value(argv, i, opt))
            if value not in {0, 1, 2, 3}:
                raise PRCError(f"Invalid Point similarity : {value}")
            data_config.pointDataConfig.simType = PointSimilarityEnum(value)
            i += 2
        elif opt == "adjNodeOffset":
            data_config.adjDataConfig.nodeOffset = int(_require_value(argv, i, opt))
            i += 2
        elif opt == "tiloMaxIteration":
            value = int(_require_value(argv, i, opt))
            if value < 0:
                raise PRCError(f"Invalid max iterations : {value}")
            policy.tiloPolicy.maxIterations = value
            i += 2
        elif opt == "tiloEpsilon":
            value = float(_require_value(argv, i, opt))
            if value < 0:
                raise PRCError(f"Invalid tilo epsilon : {value}")
            policy.tiloPolicy.tiloEpsilon = value
            i += 2
        elif opt == "policyPRCRecurseTILO":
            policy.prcRecurseTILO = _as_bool(_require_value(argv, i, opt), opt)
            i += 2
        elif opt == "policyReverseOrderOnSplit":
            policy.reverseOrderOnSplit = _as_bool(_require_value(argv, i, opt), opt)
            i += 2
        elif opt == "policyReturnRecursiveOrder":
            policy.prcReturnRecursiveOrder = _as_bool(_require_value(argv, i, opt), opt)
            i += 2
        elif opt == "policyPRCMetric":
            value = int(_require_value(argv, i, opt))
            if value not in {0, 1, 2, 3}:
                raise PRCError(f"Invalid prcMetric : {value}")
            policy.metric = PrcMetricEnum(value)
            i += 2
        elif opt == "policyRefineTILO":
            policy.prcRefineTILO = _as_bool(_require_value(argv, i, opt), opt)
            i += 2
        elif opt == "policyEvalAllMetrics":
            policy.prcEvalAllMetrics = _as_bool(_require_value(argv, i, opt), opt)
            i += 2
        elif opt == "policyReturnMetrics":
            policy.prcReturnMetrics = _as_bool(_require_value(argv, i, opt), opt)
            i += 2
        elif opt == "knnAdjMode":
            value = int(_require_value(argv, i, opt))
            if value not in {0, 1, 2, 3}:
                raise PRCError(f"Invalid knn adj mode : {value}")
            knn_policy.mode = KNNAdjMode(value)
            i += 2
        elif opt == "knnAdjK":
            value = int(_require_value(argv, i, opt))
            if value < -1:
                raise PRCError(f"Invalid knn k value : {value}")
            knn_policy.k = value
            i += 2
        elif opt == "knnAdjSigma":
            knn_policy.sigma = float(_require_value(argv, i, opt))
            i += 2
        elif opt == "gausssimAdjMode":
            value = int(_require_value(argv, i, opt))
            if value not in {0, 1}:
                raise PRCError(f"Invalid gaussian similarity adj mode : {value}")
            gauss_policy.mode = GaussSimAdjMode(value)
            i += 2
        elif opt == "gausssimAdjSigma":
            gauss_policy.sigma = float(_require_value(argv, i, opt))
            i += 2
        elif opt == "gausssimAdjThreshold":
            gauss_policy.threshold = float(_require_value(argv, i, opt))
            i += 2
        else:
            print_usage = True
            break

    return print_usage, output_file_name


# --- PLACEHOLDER_READDATA ---


def readData(
    knn_policy: KnnAdjPolicyStruct,
    gauss_policy: GaussAdjPolicyStruct,
    run_config: RunConfigStruct,
    data_config: DataConfigStruct,
) -> Tuple[object, np.ndarray, np.ndarray]:
    """根据配置读取输入数据并构建相似度矩阵"""
    if not data_config.inputFileName:
        raise PRCError("No input filename provided.")
    data = np.zeros((0, 0), dtype=float)
    vertex_weights = np.zeros((0, 0), dtype=float)
    if data_config.fileType == FileStructureEnum.POINT_DATA:
        data = loadtxt_matrix(
            data_config.inputFileName,
            comma_separated=data_config.commaSeparated,
            comment_delimiter=data_config.commentDelimiter,
        )
        points = _slice_tags(data, data_config.pointDataConfig.tagLoc)
        if data_config.pointDataConfig.simType == PointSimilarityEnum.GAUSS_ADJ_SIM:
            graph_config = GraphBuildConfig(
                similarity="gauss",
                use_sparse=data_config.useSparseMatrix,
                gauss_sigma=gauss_policy.sigma,
                gauss_mode=gauss_policy.mode,
                gauss_threshold=gauss_policy.threshold,
            )
        elif data_config.pointDataConfig.simType == PointSimilarityEnum.KNN_ADJ_SIM:
            graph_config = GraphBuildConfig(
                similarity="knn",
                use_sparse=data_config.useSparseMatrix,
                knn_k=knn_policy.k,
                knn_mode=knn_policy.mode,
                knn_sigma=knn_policy.sigma,
            )
        else:
            raise PRCError(
                f"Need to specify gaussian or knn point similarity. Not able to use {data_config.pointDataConfig.simType.name}."
            )
        storage, graph_meta = build_similarity_matrix_from_points(points, graph_config)
        matrix = storage.sparseMatrix if data_config.useSparseMatrix else storage.adjMatrix
        if matrix is None:
            raise PRCError("Failed to build similarity matrix.")
        if run_config.verboseLevel > 2:
            if "gauss_sigma_used" in graph_meta and gauss_policy.sigma <= 0:
                print(f"using Gaussian similarity sigma of {graph_meta['gauss_sigma_used']}")
            if "knn_meta" in graph_meta and knn_policy.k <= 0:
                print(f"using {int(graph_meta['knn_meta'])} nearest neighbor similarity.")
    elif data_config.fileType == FileStructureEnum.ADJACENCY_DATA:
        matrix, vertex_weights = (
            loadSparseGraph(data_config.inputFileName, data_config.adjDataConfig.nodeOffset)
            if data_config.useSparseMatrix
            else loadGraph(data_config.inputFileName, data_config.adjDataConfig.nodeOffset)
        )
    else:  # pragma: no cover
        raise PRCError("Unknown fileType.")

    if run_config.verboseLevel > 0:
        if data_config.useSparseMatrix:
            nnz = MatrixStorage(matrix).nnz()
            print(f"Sparse Graph size = {matrix.shape[0]}x{matrix.shape[1]} with {nnz}")
        else:
            print(f"Dense Graph size = {matrix.shape[0]}x{matrix.shape[1]}")
    return matrix, data, vertex_weights


def _usage_lines_pinch() -> str:
    return (
        "usage: pinchRatioClustering.py [long options] [filename [numberOfPartitions]]\n"
        "Options include --seed --numpart --verbose --saveOrder --saveLabels\n"
        "--fileType --dataInput --useSparseMatrix --pointSimilarity --tagLoc\n"
        "--knnAdjMode --knnAdjK --knnAdjSigma --gausssimAdjMode --gausssimAdjSigma\n"
        "--gausssimAdjThreshold --tiloMaxIteration --tiloEpsilon --policyPRCMetric\n"
        "--policyPRCRecurseTILO --policyReverseOrderOnSplit --policyReturnRecursiveOrder\n"
        "--policyRefineTILO --policyEvalAllMetrics --policyReturnMetrics\n"
    )


def _usage_lines_gen() -> str:
    return (
        "usage: genSimMatrix.py [long options] [filename outputFileName]\n"
        "Options are shared with pinchRatioClustering.py.\n"
    )


# --- PLACEHOLDER_CLI_ENTRY ---


def run_pinch_ratio_clustering_cli(argv: Sequence[str]) -> int:
    """pinchRatioClustering 命令行入口"""
    policy = PrcPolicyStruct()
    knn_policy = KnnAdjPolicyStruct()
    gauss_policy = GaussAdjPolicyStruct()
    run_config = RunConfigStruct()
    data_config = DataConfigStruct()

    try:
        print_usage, _ = process_cmd_line(
            argv, policy, knn_policy, gauss_policy, run_config, data_config, gen_sim_mode=False
        )
    except Exception as exc:
        print(exc)
        print(_usage_lines_pinch())
        return 2

    if print_usage or not data_config.inputFileName:
        print(_usage_lines_pinch())
        return 2

    if run_config.verboseLevel > 0:
        print("Run Configuration:")
        print(run_config.Print("   "), end="")
        print("Data Configuration:")
        print(data_config.Print("   "), end="")
        print("Current Policy:")
        print(policy.Print("   "), end="")
        print("Current KNN Adj Policy:")
        print(knn_policy.Print("   "), end="")
        print("Current Gaussian Similarity Adj Policy:")
        print(gauss_policy.Print("   "), end="")

    try:
        matrix_np, data, _ = readData(knn_policy, gauss_policy, run_config, data_config)
    except Exception as exc:
        print(f"Failed to process input data file : {data_config.inputFileName}")
        print(exc)
        return 2

    matrix = MatrixStorage(matrix_np)
    if run_config.seed == 0:
        _GLOBAL_C_RAND.srand(int(time.time()))
    else:
        _GLOBAL_C_RAND.srand(run_config.seed)

    num_parts = run_config.numberOfPartitions
    graph_file_name = data_config.inputFileName
    cluster_output_name = (
        f"{graph_file_name}{run_config.outputLabelSuffix}{num_parts}{run_config.infoSuffix}"
        + (f"_seed_{run_config.seed}" if run_config.seedSuffix else "")
    )
    mrl_output_name = f"{cluster_output_name}_multirun_labels"
    mri_output_name = f"{cluster_output_name}_multirun_info"
    order_output_name = (
        f"{graph_file_name}{run_config.outputOrderSuffix}{num_parts}{run_config.infoSuffix}"
        + (f"_seed_{run_config.seed}" if run_config.seedSuffix else "")
    )

    n = matrix.rows()
    try:
        have_initial_order, my_order = initOrder_from_files(n, run_config)
    except Exception as exc:
        print(exc)
        return 2

    best_labels = np.zeros(n, dtype=int)
    best_boundary: List[float] = []
    best_order = my_order.clone()
    best_counts = PrcReturnStruct()
    best_orun = 0
    pr_purity: List[Tuple[float, float]] = []

    out_mrl = open(mrl_output_name, "w", encoding="utf-8") if run_config.saveMultipleRuns else None
    out_mri = open(mri_output_name, "w", encoding="utf-8") if run_config.saveMultipleRuns else None
    try:
        for orun in range(run_config.numberInitOrderings):
            if (orun > 0) or (not have_initial_order):
                my_order = initOrder_random(n)
            labels = np.zeros(n, dtype=int)
            if run_config.useMultiLevelPRC:
                print("WARNING: multilevel PRC is undergoing revisions. Do not use. Exiting.")
                return 2
            counts, labels = pinchRatioClustering_storage(matrix, my_order, num_parts, policy)
            cur_boundary = sorted(my_order.boundary().data(), reverse=True)

            if run_config.saveMultipleRuns and out_mrl is not None and out_mri is not None:
                out_mrl.write(" ".join(str(int(v)) for v in labels.tolist()) + "\n")
                if data_config.fileType == FileStructureEnum.POINT_DATA and data_config.pointDataConfig.tagLoc != TagModeEnum.NO_TAGS:
                    true_tags = (
                        data[:, 0].astype(int)
                        if data_config.pointDataConfig.tagLoc == TagModeEnum.FRONT_TAGS
                        else data[:, -1].astype(int)
                    )
                    accuracy = calcPurity(labels.tolist(), true_tags.tolist())
                    out_mri.write(f"   purity = {accuracy}\n")
                    pr_purity.append((counts.averageWeightedClusterQuality, accuracy))
                out_mri.write(counts.Print(" ", ","))
                out_mri.write("  vorder = " + my_order.Print() + "\n")
                out_mri.write("  boundary =\n")
                for idx, value in enumerate(my_order.boundary().data()):
                    if idx % 10 == 0:
                        out_mri.write("\n")
                    out_mri.write(f"{value:10.6f}")
                out_mri.write("\n")
                out_mri.write("marks = " + PrintMarks(my_order.marks()) + "\n\n")
                out_mri.write("  width = " + " ".join(str(v) for v in cur_boundary) + "\n")

            if (orun == 0) or cless(counts, best_counts, cur_boundary, best_boundary):
                best_labels = labels.copy()
                best_counts = counts
                best_boundary = list(cur_boundary)
                best_order = my_order.clone()
                best_orun = orun
    finally:
        if out_mri is not None:
            out_mri.close()
        if out_mrl is not None:
            out_mrl.close()

    if run_config.saveLabels:
        with open(cluster_output_name, "w", encoding="utf-8") as fout:
            for value in best_labels.tolist():
                fout.write(f"{int(value)}\n")

    if run_config.saveOrder:
        with open(order_output_name, "w", encoding="utf-8") as fout:
            fout.write("order = " + best_order.Print() + "\n")
            fout.write("boundary = " + best_order.boundary().Print() + "\n")
            fout.write("marks = " + PrintMarks(best_order.marks()) + "\n")
            fout.write("labels = " + " ".join(str(int(v)) for v in best_labels.tolist()) + "\n")
            fout.write(f"run {best_orun} best out of {run_config.numberInitOrderings} runs.\n")

    if run_config.verboseLevel > 0:
        print("Finished with results:")
        print("   labels = " + " ".join(str(int(v)) for v in best_labels.tolist()))
        if data_config.fileType == FileStructureEnum.POINT_DATA and data_config.pointDataConfig.tagLoc != TagModeEnum.NO_TAGS:
            if run_config.verboseLevel > 5:
                print("pr purity vector = " + ",".join(f"{p[0]} {p[1]}" for p in pr_purity))
            true_tags = (
                data[:, 0].astype(int)
                if data_config.pointDataConfig.tagLoc == TagModeEnum.FRONT_TAGS
                else data[:, -1].astype(int)
            )
            if run_config.verboseLevel > 1:
                accuracy = calcPurity(best_labels.tolist(), true_tags.tolist())
                print(
                    f"{accuracy} | {best_counts.Print(' ', ',')} # {cluster_output_name} # ACCACC --- for grep'ing"
                )
                print(f"{accuracy} = purity")
        print("")

    if have_initial_order and run_config.useMultiLevelPRC:
        print("Warning: multilevel PRC currently ignores provided initial order.")
    return 0


def run_gen_sim_matrix_cli(argv: Sequence[str]) -> int:
    """genSimMatrix 命令行入口"""
    policy = PrcPolicyStruct()
    knn_policy = KnnAdjPolicyStruct()
    gauss_policy = GaussAdjPolicyStruct()
    run_config = RunConfigStruct(verboseLevel=0)
    data_config = DataConfigStruct(useSparseMatrix=True)

    try:
        print_usage, output_file_name = process_cmd_line(
            argv, policy, knn_policy, gauss_policy, run_config, data_config, gen_sim_mode=True
        )
    except Exception as exc:
        print(exc)
        print(_usage_lines_gen())
        return 2

    if print_usage or not data_config.inputFileName:
        print(_usage_lines_gen())
        return 2

    try:
        matrix, _, _ = readData(knn_policy, gauss_policy, run_config, data_config)
    except Exception as exc:
        print(exc)
        return 2

    if data_config.fileType == FileStructureEnum.ADJACENCY_DATA:
        print("Only works on point data.")
        return 2

    storage = MatrixStorage(matrix)
    if storage.adjMatrix is not None:
        dense = np.asarray(storage.adjMatrix, dtype=float)
    elif storage._sparse_kind == "custom":
        dense = storage.sparseMatrix.to_dense()  # type: ignore[union-attr]
    else:
        dense = np.asarray(storage.sparseMatrix.toarray(), dtype=float)  # type: ignore[union-attr]
    with open(output_file_name, "w", encoding="utf-8") as fout:
        for r in range(dense.shape[0]):
            for c in range(dense.shape[1]):
                value = float(dense[r, c])
                fout.write(f" {value}")
                if value > 1.0:
                    print(f"!!!! similarity greater than 1 at A[{r}, {c}] = {value}")
                    return 2
            fout.write("\n")
    return 0
