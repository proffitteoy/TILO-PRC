# pyprc

PRC/TILO 聚类算法的纯 Python 实现包。

## 模块说明

| 模块 | 职责 |
|------|------|
| `enums.py` | 枚举类型与基础数据结构（FlatStruct、PRCError） |
| `structs.py` | 策略配置与返回结果数据类 |
| `rng.py` | C++ 兼容确定性随机数生成器 |
| `matrix.py` | 矩阵存储抽象（稠密/稀疏）与边界对象 |
| `order.py` | 线性顺序对象（OrderObject、VirtualOrderObject） |
| `similarity.py` | 相似度矩阵构建（高斯、KNN） |
| `io.py` | 数据文件读取（文本矩阵、METIS 图格式） |
| `algorithm.py` | TILO 排序与 PRC 递归二分聚类核心算法 |
| `cli.py` | 命令行参数解析与 CLI 入口函数 |
| `compat.py` | 旧版 C++ 扩展兼容函数（已标记弃用） |
| `core.py` | 重导出层，保持旧导入路径兼容 |

## 依赖关系

```
enums（无依赖）
├── structs
├── rng（无依赖）
├── matrix → order / similarity / io
├── algorithm（依赖 enums, structs, rng, matrix, order）
├── cli（依赖所有模块）
└── compat（依赖 algorithm, order, matrix）
```
