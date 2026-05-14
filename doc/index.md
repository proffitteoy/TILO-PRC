# PRC 文档索引

`doc/` 目录是当前仓库的主文档入口，内容已经统一为中文，并按“纯 Python 主线”重写。

这里的文档只描述当前仓库真实保留的内容：

- 论文背景与算法思路
- Python 实现的目录结构与模块职责
- 命令行入口、参数与输出规则
- 迁移边界、验证范围与审查建议

说明：

- 仓库目录名是 `doc/`，不是 `docs/`
- 本目录下的两篇 PDF 是论文原文，作为参考资料保留，仍为英文

## 建议阅读顺序

1. [论文核心与项目思路](论文核心与项目思路.md)
2. [代码组织](代码组织.md)
3. [主线模块拆分说明](主线模块拆分说明.md)
4. [启动逻辑](启动逻辑.md)
5. [Python全量迁移说明](Python全量迁移说明.md)

## 文档清单

- [论文核心与项目思路](论文核心与项目思路.md)：论文问题定义、算法直觉和当前实现对应关系
- [代码组织](代码组织.md)：当前仓库目录、入口、核心模块与兼容层
- [主线模块拆分说明](主线模块拆分说明.md)：按主流程拆解模块职责
- [启动逻辑](启动逻辑.md)：运行方式、参数分组、输出规则与排错顺序
- [实验设计原则](实验设计原则.md)：如何用当前 Python 版本做可复现实验
- [强前置条件约束](强前置条件约束.md)：源码里真实存在的输入与参数限制
- [审查代码](审查代码.md)：针对当前 Python 主线的审查清单
- [Python全量迁移说明](Python全量迁移说明.md)：迁移范围、兼容策略、验证边界与残留风险

## 论文原文

- `Jesse_Pinch Ratio Clustering from a Topologically Intrinsic Lexicographic Ordering.pdf`
- `Jesse Johnson_Topological graph clustering with thin decomposition.pdf`

## 术语对照

- TILO：Topologically Intrinsic Lexicographic Ordering，拓扑内在字典序排序
- PRC：Pinch Ratio Clustering，基于 pinch ratio 的聚类切分
- Boundary Width：对线性顺序前缀计算得到的边界宽度序列
- Pinch Cluster：满足局部不可改进约束的候选簇结构
