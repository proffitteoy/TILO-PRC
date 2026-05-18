===========================
PRC/TILO 纯 Python 版本说明
===========================

本仓库当前保留的是 **PRC（Pinch Ratio Clustering）/ TILO（Topologically Intrinsic
Lexicographic Ordering）** 的纯 Python 实现。

目标
====

本次整理后的仓库目标很明确：

- 只保留可直接运行的 Python 主实现
- 删除旧的 C++ 主程序、历史构建脚本和无关说明
- 把仓库内项目文档统一改成中文
- 保留论文 PDF 作为算法来源材料

说明
====

这次迁移的目标是“按原仓库算法结构重建可运行实现”，不是“已经完成形式化等价证明”。

当前状态可以明确说清楚：

- 已完成主流程迁移：数据读取、相似度构图、TILO、PRC 递归切分、命令行入口
- 已完成兼容入口：`import pyprc` 与 `import prc`
- 已完成基础验证：样例数据与 CLI 冒烟运行
- 尚不能声称与历史 C++ 版本在所有输入、所有分支上逐位完全一致

如果要把“逻辑一致”提升到可以严格背书的程度，需要继续做两类工作：

1. 建立同一输入下的 C++/Python 黄金结果对照集
2. 对递归分支、边界更新和多次初始化路径做系统回归测试

仓库结构
========

::

    prc_v0.1.05_d2013_04_30/
    ├─ src/pyprc/                    Python 主实现
    ├─ datasets/                    数据集与样例输入
    ├─ doc/                      中文文档与论文 PDF
    ├─ pinchRatioClustering.py   CLI 入口
    ├─ genSimMatrix.py           CLI 入口
    ├─ prc.py                    兼容导出入口
    ├─ pyproject.toml            打包配置
    └─ COPYING.GPL               GPL 许可证

安装
====

建议环境：

- Python 3.10+
- `numpy`
- `scipy` 可选

示例：

::

    python -m pip install -e .

命令行入口
==========

安装后或在仓库根目录下，可使用以下入口：

- `pinchRatioClustering`
- `genSimMatrix`

也可以直接运行脚本：

::

    python pinchRatioClustering.py --dataInput datasets/graphs/d1.txt --fileType 1 --adjNodeOffset 0 --numpart 2

::

    python genSimMatrix.py datasets/iris/iris_all.txt datasets/iris/iris_sim_out.txt --fileType 0 --tagLoc 1

Python API
==========

推荐导入方式：

::

    import pyprc

兼容旧代码的导入方式：

::

    import prc

最小示例：

::

    import numpy as np
    import pyprc

    a = np.array([
        [0, 1, 1, 0],
        [1, 0, 0, 1],
        [1, 0, 0, 1],
        [0, 1, 1, 0],
    ], dtype=float)

    order = pyprc.OrderObject(4)
    labels = [0] * 4
    result = pyprc.pinchRatioClustering(
        a,
        order,
        labels,
        2,
        pyprc.prcPolicyStruct(),
    )

    print(labels)
    print(result)

文档
====

中文文档位于 `doc/` 目录，建议阅读顺序：

1. `doc/index.md`
2. `doc/论文核心与项目思路.md`
3. `doc/代码组织.md`
4. `doc/启动逻辑.md`
5. `doc/Python全量迁移说明.md`

论文原文
========

`doc/` 下保留了两篇原始论文 PDF。它们属于上游参考材料，因此仍为英文原文，没有做全文翻译。

许可证
======

本仓库沿用原项目许可证：GPL-3.0-or-later。详见 `COPYING.GPL`。


