# PRC — Pinch Ratio Clustering

基于拓扑内在字典序排序（TILO）的 Pinch Ratio 聚类算法纯 Python 实现。

## 环境要求

- Python 3.10+
- `numpy >= 1.23`
- `scipy >= 1.9`（可选，用于稀疏矩阵支持）

## 快速开始

### 邻接图聚类

```bash
python pinchRatioClustering.py --dataInput tests/d1.txt --fileType 1 --adjNodeOffset 0 --useSparseMatrix 1 --numpart 2
```

### 点数据聚类

```bash
python pinchRatioClustering.py --dataInput tests/iris_all.txt --fileType 0 --tagLoc 1 --pointSimilarity 2 --knnAdjMode 3 --knnAdjK -1 --numpart 3
```

### 生成相似度矩阵

```bash
python genSimMatrix.py tests/iris_all.txt output.txt --fileType 0 --tagLoc 1
```

### Iris 对比实验（PRC vs K-Means / DBSCAN / HDBSCAN）

```bash
python experiments/compare_iris_prc_baselines.py --data tests/iris_all.txt --seed 42 --prc-runs 10
```

输出文件默认在 `experiments/output/`：

- `iris_compare_metrics.csv`
- `iris_compare_metrics.json`
- `iris_compare_ari.png`

说明：

- 脚本默认可运行 `PRC + K-Means + DBSCAN`（仅依赖 `numpy` 与本仓库 `pyprc`）。
- 若环境中已安装 `hdbscan` 或 `sklearn.cluster.HDBSCAN`，会自动纳入 HDBSCAN 对比。

### 论文图复现实验（Iris + Vote）

```bash
python experiments/reproduce_paper_fig_ari.py --paper-profile
```

说明：

- `--paper-profile` 会启用当前仓库中已确认的历史 C++/论文风格 PRC 配置：`raw + gauss + sparse + recurse/refine`。
- `Vote` 默认读取仓库根目录 `house-votes-84.data`，并按论文说明默认使用 `--vote-missing-strategy drop_rows`（删除含缺失属性的样本）。
- 如需对照旧实验，也可切换 `--vote-missing-strategy` 为 `half`、`zero`、`one` 或 `column_mode`。
- 该脚本会把本次运行实际使用的 PRC policy 和 `Vote` 缺失值处理策略写入诊断 JSON，便于对照论文结果排查差异。

### Iris + TILO 一次循环切分可视化

```bash
python iris_tilo_one_loop_demo.py --data tests/iris_all.txt --output-dir outputs/iris_tilo_demo --seed 42 --knn-k -1
```

该脚本会输出：

- `outputs/iris_tilo_demo/iris_tilo_prc_one_loop.png`：四宫格可视化（Iris 分布、TILO 边界曲线、第一次切分结果、一次循环队列状态）
- `outputs/iris_tilo_demo/iris_tilo_prc_one_loop_summary.json`：一次循环关键指标与切分位置摘要

## 仓库结构

```
├── pyprc/                  # 核心 Python 包
│   ├── enums.py            # 枚举与基础类型
│   ├── structs.py          # 配置/策略数据类
│   ├── rng.py              # 确定性随机数
│   ├── matrix.py           # 矩阵存储与边界对象
│   ├── order.py            # 排序对象
│   ├── similarity.py       # 相似度矩阵构建
│   ├── io.py               # 文件读写
│   ├── algorithm.py        # TILO/PRC 核心算法
│   ├── cli.py              # 命令行接口
│   ├── compat.py           # 旧版兼容（已弃用）
│   └── core.py             # 重导出层
├── tests/                  # 测试用例与数据
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
