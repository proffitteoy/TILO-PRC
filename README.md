# PRC — Pinch Ratio Clustering

基于拓扑内在字典序排序（TILO）的 Pinch Ratio 聚类算法纯 Python 实现。

## 环境要求

- Python 3.10+
- `numpy >= 1.23`
- `scipy >= 1.9`（可选，用于稀疏矩阵支持）

## 快速开始

### 邻接图聚类

```bash
python pinchRatioClustering.py --dataInput datasets/graphs/d1.txt --fileType 1 --adjNodeOffset 0 --useSparseMatrix 1 --numpart 2
```

### 点数据聚类

```bash
python pinchRatioClustering.py --dataInput datasets/iris/iris_all.txt --fileType 0 --tagLoc 1 --pointSimilarity 2 --knnAdjMode 3 --knnAdjK -1 --numpart 3
```

### 生成相似度矩阵

```bash
python genSimMatrix.py datasets/iris/iris_all.txt output.txt --fileType 0 --tagLoc 1
```

### Iris 对比实验（PRC vs K-Means / DBSCAN / HDBSCAN）

```bash
python experiments/graph_clustering/compare_iris_prc_baselines.py --data datasets/iris/iris_all.txt --seed 42 --prc-runs 10
```

输出文件默认在 `outputs/experiments/`：

- `iris_compare_metrics.csv`
- `iris_compare_metrics.json`
- `iris_compare_ari.png`

说明：

- 脚本默认可运行 `PRC + K-Means + DBSCAN`（仅依赖 `numpy` 与本仓库 `pyprc`）。
- 若环境中已安装 `hdbscan` 或 `sklearn.cluster.HDBSCAN`，会自动纳入 HDBSCAN 对比。

### 论文图复现实验（Iris + Vote）

```bash
python experiments/graph_clustering/reproduce_paper_fig_ari.py --paper-profile
```

说明：

- `--paper-profile` 当前会启用：`raw + gauss + sparse + vote(drop_rows)`；不会强制打开 `recurse/refine`，除非显式传入对应 CLI 开关。
- `Vote` 会按顺序尝试 `--vote-data`、仓库根目录 `house-votes-84.data`、`datasets/vote/house-votes-84.data`；论文配置默认使用 `--vote-missing-strategy drop_rows`（删除含缺失属性的样本）。
- 如需对照旧实验，也可切换 `--vote-missing-strategy` 为 `half`、`zero`、`one` 或 `column_mode`。
- seeded baseline 初始化（`K Means / Spectral / DBScan / Aff. Prop. / Mean Shift`）默认启用 label block permutation；如需关闭可使用 `--no-label-permutations-for-seeded-baselines`。
- 该脚本会把本次运行实际使用的 PRC policy 和 `Vote` 缺失值处理策略写入诊断 JSON，便于对照论文结果排查差异。

### Iris + TILO 一次循环切分可视化

```bash
python experiments/demos/iris_tilo_one_loop_demo.py --data datasets/iris/iris_all.txt --output-dir outputs/demos/iris_tilo_demo --seed 42 --knn-k -1
```

该脚本会输出：

- `outputs/demos/iris_tilo_demo/iris_tilo_prc_one_loop.png`：四宫格可视化（Iris 分布、TILO 边界曲线、第一次切分结果、一次循环队列状态）
- `outputs/demos/iris_tilo_demo/iris_tilo_prc_one_loop_summary.json`：一次循环关键指标与切分位置摘要

### 传播树图网络聚类实验（PostgreSQL）

```bash
python experiments/graph_clustering/run_propagation_tree_graph_clustering.py --source-code-dir "F:\谣言传播\code" --numpart 2
```

说明：

- 脚本会从 `--source-code-dir` 下按 `.env.local -> .env -> .env.example` 顺序读取 PostgreSQL 配置（可由命令行参数覆盖）。
- 默认自动选择节点数最大的 `root_id` 拉取完整传播树；也可通过 `--root-id` 指定目标传播树。
- 以传播路径（`parent -> child`）为边、节点为点、相对时间为边权（默认 `relative_root_seconds`）进行图网络初始化。
- 输出文件默认写入 `outputs/graph_clustering/propagation_tree_graph/`，包含：
  - `*_weighted_tree.metis`：PRC 可读取的加权图文件
  - `*_nodes.tsv`：完整节点表（含时间、深度、索引）
  - `*_edges.tsv`：完整边表（含边权与相对时间）
  - `*_experiment_summary.json`：完整性校验与聚类摘要
- 默认会自动调用 PRC 聚类；若只需构图可添加 `--skip-prc`。

### 谣言 vs 非谣言传播树可视化（SVG）

```bash
python experiments/graph_clustering/visualize_rumor_nonrumor_trees.py --source-code-dir "F:\谣言传播\code"
```

说明：

- 输出目录：`outputs/graph_clustering/rumor_vs_non_rumor_viz/`
- 产物包括：
  - `sample_trees_panel.svg`：谣言/非谣言样例传播树面板图
  - `*_boxplot.svg`：节点数、时长、深度、分支因子、父子时延等指标分布对比
  - `tree_metrics.tsv`：每棵传播树的结构指标明细
- `visualization_summary.json`：本次抽样配置与文件索引

### 谣言 vs 非谣言 PRC 聚类研究（批量）

```bash
python experiments/graph_clustering/run_rumor_nonrumor_prc_study.py --source-code-dir "F:\谣言传播\code" --numpart 2
```

说明：

- 脚本会为每棵传播树构建加权图（默认边权 `relative_root_seconds`），并运行 PRC。
- 默认跑全量 rumor/non_rumor（不按树大小分类）；可用 `--max-per-label` 限制每类数量。
- 输出目录默认：`outputs/graph_clustering/prc_study_rumor_nonrumor/all_trees/`
- 关键产物：
  - `roots_catalog.tsv`：本次任务清单（固定 root 列表）
  - `per_tree_prc_metrics.tsv`：每棵树的聚类指标（`cut_ratio`、`ncut`、`cluster_entropy_norm`、`largest_cluster_ratio` 等）
  - `errors.tsv`：失败 root 与错误信息
  - `checkpoint.json`：当前进度（支持中断恢复）
  - `study_summary.json`：按 rumor/non_rumor 分组后的统计汇总
- 断点恢复：
  - 直接重复执行同一条命令即可自动跳过已完成 root（默认 `--resume` 开启）。
  - 如需重试失败项可加 `--retry-errors`。

## 仓库结构

```
├── src/
│   └── pyprc/              # 核心 Python 包
│       ├── enums.py        # 枚举与基础类型
│       ├── structs.py      # 配置/策略数据类
│       ├── rng.py          # 确定性随机数
│       ├── matrix.py       # 矩阵存储与边界对象
│       ├── order.py        # 排序对象
│       ├── similarity.py   # 相似度矩阵构建
│       ├── io.py           # 文件读写
│       ├── algorithm.py    # TILO/PRC 核心算法
│       ├── cli.py          # 命令行接口
│       ├── compat.py       # 旧版兼容（已弃用）
│       └── core.py         # 重导出层
├── datasets/               # 数据集（支持分子目录）
├── experiments/            # 实验脚本（含 demos）
├── outputs/                # 输出产物（支持分子目录）
├── doc/                    # 中文文档
├── pinchRatioClustering.py # 聚类脚本入口
├── genSimMatrix.py         # 相似度矩阵脚本入口
├── prc.py                  # 旧版兼容导入
└── pyproject.toml          # 包配置
```

## 文档

详细文档见 `doc/` 目录，建议阅读顺序：

1. [论文核心与项目思路](doc/论文核心与项目思路.md)
2. [代码组织](doc/代码组织.md)
3. [主线模块拆分说明](doc/主线模块拆分说明.md)
4. [启动逻辑](doc/启动逻辑.md)

## 许可证

GPL-3.0-or-later

