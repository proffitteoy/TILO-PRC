# 测试

本目录包含 PRC/TILO 的测试用例和测试数据。

## 测试数据

- `d1.txt` — 6 节点图数据（METIS 格式）
- `d1_initialorder.txt` — d1 的初始顺序
- `iris_all.txt` — Iris 数据集（带标签）

## 运行测试

```bash
python -m unittest discover tests -v
```
