# Python 全量迁移说明

本文档描述当前仓库从早期 C++ 代码库整理为纯 Python 主线后的实现边界。

## 迁移目标

迁移目标不是“保留所有历史文件”，而是：

- 保留论文主流程
- 保留主要公开接口
- 去掉 C++ 编译依赖
- 让仓库在现代 Python 环境下可直接运行

## 当前保留的实现范围

已经迁移并可运行的主流程包括：

1. 数据读取
2. 点数据到图的构造
3. TILO 顺序优化
4. PRC 切分
5. 命令行主程序
6. 基础兼容 API

对应入口：

- `src/pyprc/core.py`
- `pinchRatioClustering.py`
- `genSimMatrix.py`
- `prc.py`

## 接口映射

主要结构和函数在 Python 中保留了接近原仓库的命名：

- `BoundaryObject`
- `FlatStruct`
- `OrderObject`
- `PrcPolicyStruct`
- `TiloPolicyStruct`
- `RunConfigStruct`
- `DataConfigStruct`
- `gaussSimMatrix`
- `knnSimMatrix`
- `TILO`
- `RefineTILO`
- `findSplitLocation`
- `pinchRatioClustering`

另外保留了旧风格兼容别名：

- `prcPolicyStruct`
- `tiloPolicyStruct`
- `prcMetricEnum`
- `KNN_ADJ_MODE`
- `GAUSSSIM_ADJ_MODE`

## 与历史仓库的关系

可以明确区分三件事：

### 1. 算法结构已迁移

当前 Python 版本保留了原项目的核心算法链路和主要参数语义。

### 2. 仓库形态已改变

当前仓库不再以 C++ 源码和 CMake 构建为主，不再要求用户先编译再运行。

### 3. 等价性尚未被严格证明

目前不能严谨声称：

- 对所有输入都与原版输出完全相同
- 对所有边界分支都与原版逐步一致
- 对所有随机初始化路径都已完成回归验证

当前能够负责任地说的是：

- 核心流程可运行
- 常用公开接口可用
- 样例输入已通过基础验证
- 部分复杂分支仍缺少与历史实现的一一对照测试

## 已完成验证

已完成的验证属于“工程可运行验证”，主要包括：

- `import pyprc`
- `import prc`
- 邻接图输入的 CLI 运行
- 相似度矩阵生成 CLI 运行
- 基础单元测试

这些验证证明仓库可用，但不等于论文级完全复刻证明。

## 当前风险边界

最需要继续验证的部分是：

1. 递归切分时的顺序回写
2. 多次初始化后的最优解选择
3. 稀疏/稠密路径在边界情况下的一致性
4. 旧版实验性指标分支

## 如果要进一步做“原版一致性验证”

建议按下面的顺序推进：

1. 构建一组固定输入样本
2. 保存历史版本的标签、顺序、边界输出
3. 用 Python 版本逐项对比
4. 对递归和随机初始化分支单独建回归用例

只有完成这一轮对照后，才能更强地声称“与原版逻辑一致”。

