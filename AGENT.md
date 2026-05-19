# AGENT.md

## 回答与协作

- 默认使用中文回答。
- 先遵守用户当前要求，再遵守本文件，再参考仓库文档。
- 优先做最小可验证修改，不擅自大规模重构无关文件。
- 代码改动后，说明验证方式、产物路径与剩余风险。

## 当前仓库定位

本仓库是 **PRC（Pinch Ratio Clustering）纯 Python 实现与实验仓库**，核心目标是：

- 复现与扩展 TILO/PRC 聚类流程；
- 支撑 Iris/Vote/传播树等实验；
- 产出可复现实验脚本与结果文件。

不是 Web 前端项目，不是 CMS，不是通用后台模板工程。

## 目录角色

### 应优先修改

- `src/pyprc`：核心算法与数据结构实现
- `experiments`：实验脚本与研究流程
- `datasets`：实验输入数据（仅在必要时补充/清洗）
- `doc`：中文文档与实验说明
- 根目录 CLI 入口：
  - `pinchRatioClustering.py`
  - `genSimMatrix.py`
  - `prc.py`

### 默认不作为主开发目标

- `outputs`：实验产物目录。默认只新增本次实验结果，不随意改写或删除历史结果。
- `.uv-cache`、`.uv-python`：运行时缓存目录，不做业务修改。

## 技术栈与运行方式

- Python `>=3.10`
- 依赖：`numpy>=1.23`（可选 `scipy>=1.9`）
- 包配置见 `pyproject.toml`

常用命令（以 README 为准）：

- `python pinchRatioClustering.py ...`
- `python genSimMatrix.py ...`
- `python experiments/...`

## 实验开发约束

- 新实验优先放在 `experiments/` 下合适子目录（如 `experiments/graph_clustering/`）。
- 新实验输出优先写入 `outputs/` 下独立子目录，避免覆盖既有实验。
- 涉及批量任务必须考虑断点恢复（checkpoint）与可重复执行（resume）。
- 统计结论应同时给出：
  - 原始结果表（如 TSV/JSON）
  - 统计方法（检验类型、多重比较校正）
  - 结论与局限

## 文档同步

涉及算法流程、实验口径、目录约定变更时，需要同步更新文档：

- `README.md`
- `doc/index.md`
- `doc/论文核心与项目思路.md`
- `doc/代码组织.md`
- `doc/主线模块拆分说明.md`
- `doc/启动逻辑.md`

注意：本仓库文档目录是 `doc/`，不是 `docs/`。

## 提交前检查建议

- 仅包含与当前任务相关的代码和文档改动。
- 关键脚本至少做一次最小规模验证（参数冒烟或语法检查）。
- 报告类改动给出可点击的产物路径，便于复核。
