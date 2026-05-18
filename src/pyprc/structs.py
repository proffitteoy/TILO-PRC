# 策略配置与返回结果数据类
# 本模块定义 PRC/TILO 算法的所有配置结构体和返回值结构体。
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .enums import (
    FileStructureEnum,
    GaussSimAdjMode,
    KNNAdjMode,
    PointSimilarityEnum,
    PrcMetricEnum,
    TagModeEnum,
)


@dataclass
class PrcCountsStruct:
    numberOfShifts: int = 0
    numberOfInversions: int = 0
    numberOfIterations: int = 0

    def add(self, other: PrcCountsStruct) -> None:
        self.numberOfShifts += other.numberOfShifts
        self.numberOfInversions += other.numberOfInversions
        self.numberOfIterations += other.numberOfIterations

    def Print(self, indent: str = "", sep: str = "\n") -> str:
        return (
            f"{indent}number of shifts =  {self.numberOfShifts}{sep}"
            f"{indent}number of inversions =  {self.numberOfInversions}{sep}"
            f"{indent}number of iterations =  {self.numberOfIterations}{sep}"
        )


@dataclass
class PrcMetricValues:
    mincut: float = 0.0
    minmaxcutA: float = 0.0
    minmaxcutB: float = 0.0
    intA: float = 0.0
    extA: float = 0.0
    intB: float = 0.0
    extB: float = 0.0
    dA: float = 0.0
    dB: float = 0.0
    pinchRatio: float = 0.0
    ncut: float = 0.0
    relA: float = 0.0
    relB: float = 0.0
    relRatio: float = 0.0
    crossRatio: float = 0.0
    loc: int = -1

    def Print(self, indent: str = "", sep: str = "\n") -> str:
        return (
            f"{indent}mincut {self.mincut}{sep}"
            f"{indent}minmaxcutA {self.minmaxcutA}{sep}"
            f"{indent}minmaxcutB {self.minmaxcutB}{sep}"
            f"{indent}intA {self.intA}{sep}"
            f"{indent}extA {self.extA}{sep}"
            f"{indent}intB {self.intB}{sep}"
            f"{indent}extB {self.extB}{sep}"
            f"{indent}dA {self.dA}{sep}"
            f"{indent}dB {self.dB}{sep}"
            f"{indent}pinchRatio {self.pinchRatio}{sep}"
            f"{indent}ncut {self.ncut}{sep}"
            f"{indent}relA {self.relA}{sep}"
            f"{indent}relB {self.relB}{sep}"
            f"{indent}relRatio {self.relRatio}{sep}"
            f"{indent}crossRatio {self.crossRatio}{sep}"
            f"{indent}loc {self.loc}"
        )


@dataclass
class PrcReturnStruct:
    counts: PrcCountsStruct = field(default_factory=PrcCountsStruct)
    averageWeightedClusterQuality: float = 0.0
    averageClusterQuality: float = 0.0
    weightedGeometricMean: float = 0.0
    geometricMean: float = 0.0
    mvalues: List[PrcMetricValues] = field(default_factory=list)

    def Print(self, indent: str = "", sep: str = "\n") -> str:
        return self.counts.Print(indent, sep)

    def PrintVerbose(self, indent: str = "", sep: str = "\n") -> str:
        parts = [
            self.counts.Print(indent, sep),
            f"{indent}Warning: following values may not be calculated on every run:{sep}",
            f"{indent}average weighted cluster quality =  {self.averageWeightedClusterQuality}{sep}",
            f"{indent}average cluster quality =  {self.averageClusterQuality}{sep}",
            f"{indent}weighted geometric mean =  {self.weightedGeometricMean}{sep}",
            f"{indent}geometric mean =  {self.geometricMean}{sep}",
        ]
        if self.mvalues:
            metric_text = "".join(f"|{m.Print('', sep)}" for m in self.mvalues)
            parts.append(f"{indent}{metric_text}")
        return "".join(parts)


@dataclass
class TiloPolicyStruct:
    maxIterations: int = 10_000_000
    tiloEpsilon: float = 1e-12

    def Print(self, indent: str = "", sep: str = "\n") -> str:
        return (
            f"{indent}TILO maxIterations = {self.maxIterations}{sep}"
            f"{indent}TILO epsilon = {self.tiloEpsilon}{sep}"
        )


@dataclass
class PrcPolicyStruct:
    tiloPolicy: TiloPolicyStruct = field(default_factory=TiloPolicyStruct)
    metric: PrcMetricEnum = PrcMetricEnum.PinchRatio
    prcRecurseTILO: bool = False
    reverseOrderOnSplit: bool = False
    prcReturnRecursiveOrder: bool = False
    prcRefineTILO: bool = False
    prcEvalAllMetrics: bool = False
    prcReturnMetrics: bool = False

    def Print(self, indent: str = "", sep: str = "\n") -> str:
        nested = indent + indent
        return (
            f"{indent}TILO Policies : {sep}{self.tiloPolicy.Print(nested, sep)}"
            f"{indent}prcRecurseTILO = {self.prcRecurseTILO}{sep}"
            f"{indent}reverseOrderOnSplit = {self.reverseOrderOnSplit}{sep}"
            f"{indent}prcReturnRecurviseOrder = {self.prcReturnRecursiveOrder}{sep}"
            f"{indent}prcMetric = {int(self.metric)}{sep}"
            f"{indent}prcRefineTILO = {self.prcRefineTILO}{sep}"
            f"{indent}prcEvalAllMetrics = {self.prcEvalAllMetrics}{sep}"
            f"{indent}prcReturnMetrics = {self.prcReturnMetrics}{sep}"
        )


@dataclass
class GaussAdjPolicyStruct:
    mode: GaussSimAdjMode = GaussSimAdjMode.GS_ADJ_THRESHOLD
    sigma: float = -1.0
    threshold: float = 1e-10

    def Print(self, indent: str = "", sep: str = "\n") -> str:
        return (
            f"{indent}mode = {self.mode.name}{sep}"
            f"{indent}sigma = {self.sigma}{sep}"
            f"{indent}threshold = {self.threshold}{sep}"
        )


@dataclass
class KnnAdjPolicyStruct:
    mode: KNNAdjMode = KNNAdjMode.KNN_EITHER_ADJ_GAUSS
    k: int = -1
    sigma: float = -1.0

    def Print(self, indent: str = "", sep: str = "\n") -> str:
        return (
            f"{indent}mode = {self.mode.name}{sep}"
            f"{indent}k = {self.k}{sep}"
            f"{indent}sigma = {self.sigma}{sep}"
        )


@dataclass
class RunConfigStruct:
    seed: int = 0
    numberOfPartitions: int = 2
    verboseLevel: int = 1
    useTransduction: bool = False
    outputLabelSuffix: str = "_part_"
    outputOrderSuffix: str = "_tilo_"
    infoSuffix: str = ""
    saveOrder: bool = True
    saveLabels: bool = True
    seedSuffix: bool = False
    useMultiLevelPRC: bool = False
    initOrderFile: str = ""
    initLabelsFile: str = ""
    numberInitOrderings: int = 1
    saveMultipleRuns: bool = False

    def Print(self, indent: str = "") -> str:
        return (
            f"{indent}seed = {self.seed}\n"
            f"{indent}number of partitions = {self.numberOfPartitions}\n"
            f"{indent}verbose level = {self.verboseLevel}\n"
            f"{indent}use transduction = {self.useTransduction}\n"
            f"{indent}save lexical order information flag = {self.saveOrder}\n"
            f"{indent}save partition labels flag = {self.saveLabels}\n"
            f"{indent}add seed suffix flag = {self.seedSuffix}\n"
            f"{indent}outputLabelsSuffix = {self.outputLabelSuffix}\n"
            f"{indent}outputOrderSuffix = {self.outputOrderSuffix}\n"
            f"{indent}infoSuffix = {self.infoSuffix}\n"
            f"{indent}use multilevel PRC flag = {self.useMultiLevelPRC}\n"
            f"{indent}initOrderFile = {self.initOrderFile}\n"
            f"{indent}initLabelsFile = {self.initLabelsFile}\n"
            f"{indent}number of initial orderings = {self.numberInitOrderings}\n"
            f"{indent}save multiple run flag = {self.saveMultipleRuns}\n"
        )


@dataclass
class PointDataConfigStruct:
    tagLoc: TagModeEnum = TagModeEnum.NO_TAGS
    simType: PointSimilarityEnum = PointSimilarityEnum.GAUSS_ADJ_SIM

    def Print(self, indent: str = "") -> str:
        return (
            f"{indent}tag location = {self.tagLoc.name}\n"
            f"{indent}point similarity type = {self.simType.name}\n"
        )


@dataclass
class AdjDataConfigStruct:
    nodeOffset: int = 1

    def Print(self, indent: str = "") -> str:
        return f"{indent}adjacent node offset = {self.nodeOffset}\n"


@dataclass
class DataConfigStruct:
    inputFileName: str = ""
    fileType: FileStructureEnum = FileStructureEnum.POINT_DATA
    useSparseMatrix: bool = True
    commaSeparated: bool = False
    commentDelimiter: str = "#"
    pointDataConfig: PointDataConfigStruct = field(default_factory=PointDataConfigStruct)
    adjDataConfig: AdjDataConfigStruct = field(default_factory=AdjDataConfigStruct)

    def Print(self, indent: str = "") -> str:
        nested = indent + "   "
        return (
            f"{indent}data input file name = {self.inputFileName}\n"
            f"{indent}file data type = {self.fileType.name}\n"
            f"{indent}use Sparse Matrix = {self.useSparseMatrix}\n"
            f"{indent}comma separated = {self.commaSeparated}\n"
            f"{indent}comment delimiter = {self.commentDelimiter}\n"
            f"{indent}point file configuration : \n"
            f"{self.pointDataConfig.Print(nested)}"
            f"{indent}adjacency file configuration : \n"
            f"{self.adjDataConfig.Print(nested)}"
        )
